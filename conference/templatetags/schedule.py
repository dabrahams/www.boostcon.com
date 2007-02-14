# Copyright David Abrahams 2007. Distributed under the Boost
# Software License, Version 1.0. (See accompanying
# file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)
from django import template
from boost_consulting.conference.models import *
from datetime import *
from utils.format import _12hr_time

register = template.Library()

def format_time_range(t1,t2):
    from boost_consulting.utils.dom import tag as _
    if t1 == t2:
        return _12hr_time(t1)
    else:
        return (_12hr_time(t1), _.br, _12hr_time(t2))

def iterate_days(start, finish):
    for d in range(start.toordinal(), finish.toordinal()+1):
        yield date.fromordinal(d)

def day_to_datetime(day):
    return datetime(day.year, day.month, day.day)

def day_blocks(conference, day):
    day_dt = day_to_datetime(day)
    return TimeBlock.objects \
        .filter(conference = conference) \
        .filter(start__range=(day_dt,day_dt+timedelta(1)))

class Break(object):
    def __init__(self, start,finish):
        self.start = start
        self.finish = finish

def time_segments(conference, day):
    """A generator for all significant time segments on the given day.

    Returns Break instances for the segments where there's no TimeBlock.
    """
    prev_block = None
    for block in day_blocks(conference,day):
        if prev_block and prev_block.finish != block.start:
            yield Break(prev_block.finish, block.start)
        prev_block = block
        yield block

class ScheduleNode(template.Node):
    def render_schedule(self, ctx, conference):
        result = []

        tracks = Track.objects.filter(conference = conference)
        session_counters = dict([(t,0) for t in tracks])
        
        for d in iterate_days(conference.start, conference.finish):
            result.append(str(self.render_day(
                conference,d,tracks,session_counters)))

        return u'\n'.join(result).encode('utf-8')

class PrivateScheduleNode(ScheduleNode):
    def render_day(self, conference, day, tracks, session_counters):
        from boost_consulting.utils.dom import tag as _

        rows = []

        header = None
        
        for ts in time_segments(conference,day):
            row = _.tr
            
            if not rows:
                header = _.th(_class="weekday")[
                    [ _.em[ letter ] for letter in day.strftime('%A') ],
                    _.br, day.strftime('%b %d')
                    ]
                row <<= header

            range = format_time_range(ts.finish, ts.start)
            
            if isinstance(ts, Break):
                row(_class="break")
                
                # add its time header
                row <<= _.th(_class="timespan")[ range ]

                # and an empty box across all tracks
                row <<= _.td(colspan=len(tracks))[ 'break' ]
                
            else:
                row <<= _.th(_class="timespan")[
                    # I wish I knew a less-fragile way to the timeblock admin.
                    _.a(href="/admin/conference/timeblock/%s/" % ts.id)[range]
                    ]

                row <<= [ _.td[ t.name ] for t in tracks ]

            rows.append(row)

        if header:
            header(rowspan=len(rows))
            
        return u'\n'.join(str(r) for r in rows)
            
    def render(self, ctx):
        return self.render_schedule(ctx, ctx['conference'])
        
def schedule(parser, token):
    return PrivateScheduleNode()

# Not used.
class NoneIsAllDict(dict):
    def __getitem__(self, k):
        try:
            return super(NoneIsAllDict,self).__getitem__(k)
        except:
            kk, v = self.iteritems()
            if k is None:
                return v
            elif kk is None:
                return
            

class PublicScheduleNode(ScheduleNode):
    def __init__(self, conference):
        super(PublicScheduleNode,self).__init__()
        self.conference = conference

    def render(self, ctx):
        return self.render_schedule(ctx, self.conference)

    def render_day(self, conference, d, tracks, session_counters):
        from boost_consulting.utils.dom import tag as _
        
        return _.table(
            _class="table",
            summary="%s Schedule for %s" % (conference, d.strftime('%A, %B %d'))
            )[
                _.caption[ d.strftime('%A, %B %d') ]

              , _.thead[
                    _.tr[

                        # time header
                        _.th(scope="col"
                            , width="%s%%" % (28 / len(tracks))
                             )['time']

                        # track headers
                      , [
                            _.th(
                                scope="col", width="%s%%" % (86 / len(tracks))
                            )[
                               _.strong[t.name], ' track'
                            ]
                            for t in tracks
                        ]
                    ]
                ] # </THEAD>
              , self.render_day_body(conference, d, tracks, session_counters)
            ]
        
    def render_day_body(self, conference, d, tracks, session_counters):
        from boost_consulting.utils.dom import tag as _
        body = _.tbody

        # Keeps track of active sessions in each track
        active = {}
        
        sessions = Session.objects \
                   .filter(start__start__gte=day_to_datetime(d))

        for b in time_segments(conference,d):

            row = _.tr[
                _.th(scope="row")[ format_time_range(b.start,b.finish) ]
                ]

            body <<= row

            if isinstance(b, Break):
                row <<= _.td(_class="break", colspan=len(tracks))['Break']
                
            elif isinstance(b, TimeBlock):
                error = {}
                
                for s in sessions.filter(start=b):
                    if s.track:
                        existing = active.get(s.track)
                        if existing:
                            error[s.track] = (_.br, '*** overlapping with %s ***' % existing[0])

                        active[s.track] = s, s.duration
                    else:
                        if active:
                            error[tracks[0]] = (
                                _.br
                              , '*** overlapping with %s ***'
                                % ', '.join([str(a[0]) for a in
                                             active.values()]) )
                        active = dict([ (t,(s,s.duration)) for t in tracks ])

                
                for ti,t in enumerate(tracks):
                    try:
                        current,remaining = active[t]
                    except:
                        cell = _.td(valign="top")['nothing scheduled']
                        row <<= cell
                        if not active:
                            cell(colspan=len(tracks))
                            break
                        else:
                            continue
                        


                    title = current.title
                    if current.start == b:
                        session_counters[t] += 1
                        get_name = lambda p: p.full_name()
                        suffix = ''
                    else:
                        get_name = lambda p: p.last_name
                        # title = u'...%s...' % current.short_title
                        suffix = _.em[' (continued)']

                    error_class = error.get(t) and ' error' or ''
                    error_msg = error.get(t,'')

                    cell = _.td(
                        valign="top"
                      , _class='ud'[ti%2]+str(1+session_counters[t]%2) + error_class
                        )[
                                [ ( _.a(href="/program/speakers#presenter_%d" % p.id)[
                                        _.span(_class="name")[get_name(p)]
                                    ], (n and [', '] or [': '])[0])
                                  for n, p in
                                  enumerate(current.presenters.order_by('-last_name',
                                                                        '-first_name'))
                                ][::-1]

                              , _.a(href="/program/sessions#session_%d" % current.id)[title]
                              , suffix
                              , error_msg
                            ]
                    
                    row <<= cell

                    remaining -= (b.finish - b.start).seconds/60
                    if current.track:
                        if remaining <= 0:
                            del active[t]
                        else:
                            active[t] = current,remaining
                    else:
                        if remaining <= 0:
                            active = {}
                        else:
                            active = dict([ (track,(current,remaining)) for track in tracks ])
                            
                        cell(colspan = len(tracks))
                        break
                    
        return body
        
def public_schedule(parser, token):
    try:
        tag_name, conference_name,year = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires three arguments" % token.split_contents()[0]
    return PublicScheduleNode(Conference.objects.get(name=conference_name,start__year=int(year)))

register.tag(schedule)
register.tag(public_schedule)
