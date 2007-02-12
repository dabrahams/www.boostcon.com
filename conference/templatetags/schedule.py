# Copyright David Abrahams 2007. Distributed under the Boost
# Software License, Version 1.0. (See accompanying
# file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)
from django import template
from conference.models import *
from datetime import *
from utils.format import _12hr_time

register = template.Library()

def format_time_range(t1,t2):
    from boost_consulting.utils.dom import tag as _
    return (_12hr_time(t1), _.br, '-', _12hr_time(t2))

class ScheduleNode(template.Node):
    def render_day(self, conference, day):
        from boost_consulting.utils.dom import tag as _

        tracks = Track.objects.filter(conference = conference)
        
        rows = []

        header = None
        
        prev_block = None
        day_dt = datetime(day.year, day.month, day.day)
        for block in TimeBlock.objects \
            .filter(conference = conference) \
            .filter(start__range=(day_dt,day_dt+timedelta(1))):
            
            row = _.tr
            
            if not rows:
                header = _.th(_class="weekday")[
                    [ _.em[ letter ] for letter in day.strftime('%A') ],
                    _.br, day.strftime('%b %d')
                    ]
                row += header
            
            if prev_block and prev_block.finish != block.start:
                row(_class="break")
                
                # add its time header
                row += _.th(_class="timespan")[ format_time_range(prev_block.finish, block.start) ]

                # and an empty box across all tracks
                row += _.td(colspan=len(tracks))[ 'break' ]
                rows.append(row)
                row = _.tr

            row += _.th(_class="timespan")[
                # I wish I knew a less-fragile way to the timeblock admin.
                _.a(href="/admin/conference/timeblock/%s/" % block.id)[
                        format_time_range(block.start,block.finish)
                        ]
                ]
            
            for t in tracks:
                row += _.td[ t.name ]

            rows.append(row)
            prev_block = block

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
