# Copyright David Abrahams 2007. Distributed under the Boost
# Software License, Version 1.0. (See accompanying
# file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)
from models import *
from datetime import *
from format import _12hr_time

def sorted(s,f=None):
    ret = list(s)
    ret.sort(f)
    return ret

def format_time_range(t1,t2):
    from dom import tag as _
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
    return sorted(
        t for t in TimeBlock.objects.all()
        if t.conference == conference
        and t.start >= day_dt and t.start < (day_dt+timedelta(days=1))
        )

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

class ScheduleNode(object):
    def render_schedule(self, values):
        result = []

        tracks = sorted(
            [t for t in Track.objects.all() if t.conference == values.conference], 
            lambda x,y:cmp(x.name,y.name))

        session_counters = dict([(t,0) for t in tracks] + [(None,0)])
        
        for d in iterate_days(values.conference.start, values.conference.finish):
            result.append(self.render_day(
                values,d,tracks,session_counters))

        from dom import tag as _
        return _.schedule[ result ]

        
class PublicScheduleNode(ScheduleNode):
    def __init__(
        self, conference_name, 
        year, 
        presenter_base='presenter_id_', 
        session_base='session_id_'
        ):
        self.conference_name = conference_name
        self.year = year
        self.presenter_base = presenter_base
        self.session_base = session_base

    def render(self):
        class Values(object):
            def __init__(self,**kw):
                self.__dict__.update(kw)

        v = Values(
            conference=iter(Conference.objects.all()).next(),
            presenter_base = self.presenter_base + '#',
            session_base = self.session_base + '#'
        )
        
        return self.render_schedule(v)

    def render_day(self, values, d, tracks, session_counters):
        from dom import tag as _

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
                                , style="width:%s%%" % (28 / len(tracks))
                                 )['time']

                            # track headers
                          , [
                                _.th(
                                    scope="col", style="width:%s%%" % (86 / len(tracks))
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
        from dom import tag as _
        body = _.tbody
        tracks = tracks or [Track('')]

        # Keeps track of active sessions in each track
        active = {}
        
        sessions = set(
            s for s in Session.objects.all() 
            if s.start.start >=  day_to_datetime(d))

        for b in time_segments(values.conference,d):

            row = _.tr[
                _.th(scope="row")[ format_time_range(b.start,b.finish) ]
                ]

            body <<= row

            if isinstance(b, Break):
                row <<= _.td(_class="break", colspan=len(tracks))['Break']
                
            elif isinstance(b, TimeBlock):
                error = {}
                
                for s in [s for s in sessions if s.start == b]:
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
                                   enumerate(sorted(current.presenters)[::-1])
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

if __name__ == '__main__':
    import populate
    print'''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
        "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <title>Schedule</title>
  <meta http-equiv="content-type" content="text/html;charset=utf-8" />
  <link rel="stylesheet" type="text/css" href="style.css" />
  <link rel="stylesheet" type="text/css" href="final_drop.css" />
</head>
'''
    x = PublicScheduleNode('C++Now!', 2012).render()
    x.element.tag='body'
    print x
    print '''
</html>
'''
    
