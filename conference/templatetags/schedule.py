# Copyright David Abrahams 2007. Distributed under the Boost
# Software License, Version 1.0. (See accompanying
# file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)
from django import template
from django.template import resolve_variable
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
    def render_schedule(self, values):
        result = []

        tracks = Track.objects.filter(conference = values.conference).order_by('name')
        session_counters = dict([(t,0) for t in tracks] + [(None,0)])
        
        for d in iterate_days(values.conference.start, values.conference.finish):
            result.append(str(self.render_day(
                values,d,tracks,session_counters)))

        return u'\n'.join(result).encode('utf-8')

        
class PublicScheduleNode(ScheduleNode):
    def __init__(self, conference_name='params.conference', year='params.year', presenter_base='params.presenter_base', session_base='params.session_base'):
        super(PublicScheduleNode,self).__init__()
        self.conference_name = conference_name
        self.year = year
        self.presenter_base = presenter_base
        self.session_base = session_base

    def render(self, ctx):
        class Values(object):
            def __init__(self,**kw):
                self.__dict__.update(kw)

        try:
            v = Values(
            conference = Conference.objects.get(
                name=resolve_variable(self.conference_name,ctx),
                start__year=int(resolve_variable(self.year,ctx))),
            presenter_base = resolve_variable(self.presenter_base,ctx) + '#',
            session_base = resolve_variable(self.session_base,ctx) + '#',
            )
        except:
            import pprint
            pprint.pprint(ctx)
            raise
        
        return self.render_schedule(v)

    def render_day(self, values, d, tracks, session_counters):
        from boost_consulting.utils.dom import tag as _

        tracks = tracks or [Track('')]
            
        return _.table(
            _class="schedule",
            summary="%s Schedule for %s" % (values.conference, d.strftime('%A, %B %d'))
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
                               _.strong[t.name]
                            ]
                            for t in tracks
                        ]
                    ]
                ] # </THEAD>
              , self.render_day_body(values, d, tracks, session_counters)
            ]
        
    def render_day_body(
        self, values, d, tracks, session_counters
        ):
        from boost_consulting.utils.dom import tag as _
        body = _.tbody
        tracks = tracks or [Track('')]

        # Keeps track of active sessions in each track
        active = {}
        
        sessions = Session.objects \
                   .filter(start__start__gte=day_to_datetime(d))

        for b in time_segments(values.conference,d):

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
                        
                    if current.start == b:
                        link_target = _.a(id='schedule.'+current.slug())
                        if current.schedule_note:
                            title = current.title, ' ', current.schedule_note
                        else:
                            title = current.title
                        session_counters[current.track] += 1
                        get_name = lambda p: p.full_name()
                        continued = ''
                    else:
                        link_target = ''
                        title = current.short_title
                        get_name = lambda p: p.last_name
                        # title = u'...%s...' % current.short_title
                        continued = _.em[' (continued)']

                    cell_class = current.track and 'ud'[ti%2] or 'notrack'
                    cell_class += str(1+session_counters[current.track]%2)
                    if error.get(t):
                        cell_class += ' error'

                    error_msg = error.get(t,'')

                    cell = _.td(valign="top", _class=cell_class)[
                                link_target

                                # A sequence of presenter name, comma
                                # pairs... except we make the first one a
                                # colon.  Then we reverse them to put the colon
                                # at the end
                              , [
                                    (
                                      _.a(href=values.presenter_base+p.slug())
                                      [
                                         _.span(_class="name")[get_name(p)]
                                      ]
                                    , (n and [', '] or [': '])[0]
                                   )

                                   # Read the names in reverse alphabetical
                                   # order so they come out right in the end.
                                   for n, p in
                                   enumerate(current.presenters.order_by('-last_name',
                                                                        '-first_name'))
                                ][::-1] # reverse

                              , _.a(href=values.session_base+current.slug())[title]

                              , continued
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
    args = token.split_contents()[1:]
    if len(args) > 4:
        raise template.TemplateSyntaxError, (
            "%r tag requires no more than four arguments" % token.split_contents()[0])

    return PublicScheduleNode(
        **dict(zip(('conference_name','year','presenter_base','session_base'),args)))
        


register.tag(public_schedule)
