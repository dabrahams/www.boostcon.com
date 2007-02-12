# Copyright David Abrahams 2007. Distributed under the Boost
# Software License, Version 1.0. (See accompanying
# file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)
from django import template
from conference.models import *
from datetime import *

register = template.Library()

class ScheduleNode(template.Node):
    def render_day(self, conference, day):
        from boost_consulting.utils.dom import tag as _

        tracks = Track.objects.filter(conference = conference)
        
        rows = []

        header = None
        
        last_finish = None
        day_dt = datetime(day.year, day.month, day.day)
        for block in TimeBlock.objects \
            .filter(conference = conference) \
            .filter(start__range=(day_dt,day_dt+timedelta(1))):
            
            row = _.tr
            
            if not rows:
                header = _.th[
                    [ _.em[ letter ] for letter in day.strftime('%A') ]
                    ]
                row += header
            
            if last_finish and last_finish != block.start: # check for break
                # add its time header
                row += _.th[ last_finish, ' - ', block.start ]

                # and an empty box across all tracks
                row += _.td(colspan=len(tracks))[ 'break' ]
                rows.append(row)
                row = _.tr
            
            row += _.th[ block.start, ' - ', block.finish ]
            
            for t in tracks:
                row += _.td[ t.name ]

            rows.append(row)
            last_finish = block.finish

        if header:
            header(rowspan=len(rows))
            
        return u'\n'.join(str(r) for r in rows)
            
    def render(self, ctx):
        from boost_consulting.utils.dom import tag as _

        conference = ctx['conference']
        result = []

        print 'range:', range(
            conference.start.toordinal()
            , conference.finish.toordinal()+1)
            
        for d in range(
            conference.start.toordinal()
            , conference.finish.toordinal()+1):

            result.append(self.render_day(conference,
                                          date.fromordinal(d)))

        return u'\n'.join(result).encode('utf-8')
        
def schedule(parser, token):
    return ScheduleNode()

register.tag(schedule)
