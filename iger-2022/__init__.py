#!/usr/bin/python3

from renderlib import *
from easing import *

# URL to schedule.xml
scheduleUrl = 'https://cfp.fairydust.reisen/iger-2022/schedule/export/schedule.xml'

def introFrames(args):
    for frame in range(2*fps):
        yield (
            ('persons', 'style', 'opacity', 0),
            ('title', 'style', 'opacity', 0),
            *((f'star{i:02}', 'style', 'opacity', easeInQuad(min(frame-i*4, 3), 0, 1, 3) if i*4 <= frame else 0) for i in range(13))
        )

    for i in range(fps):
        yield (
            ('conflicting', 'style', 'opacity', easeOutQuad(i, 1, -1, fps)),
            ('persons', 'style', 'opacity', easeInQuad(i, 0, 1, fps)),
            ('title', 'style', 'opacity', easeInQuad(i, 0, 1, fps))
        )

    for i in range(3*fps):
        yield (
            ('conflicting', 'style', 'opacity', 0),
        )

def outroFrames(args):
    for i in range(fps):
        yield (
            ('conflicting', 'style', 'opacity', easeOutQuad(i, 1, -1, fps)),
            ('event', 'style', 'opacity', 0),
            ('fairydust', 'style', 'opacity', easeOutQuad(i, 1, -1, fps)),
            ('license', 'style', 'opacity', 0)
        )

    for i in range(fps):
        yield (
            ('conflicting', 'style', 'opacity', 0),
            ('event', 'style', 'opacity', easeInQuad(i, 0, 1, fps)),
            ('fairydust', 'style', 'opacity', 0),
            ('license', 'style', 'opacity', easeInQuad(i, 0, 1, fps))
        )

    for i in range(4*fps):
        yield (
            ('conflicting', 'style', 'opacity', 0),
            ('fairydust', 'style', 'opacity', 0)
        )

def debug():
    render('intro.svg',
        '../intro.ts',
        introFrames,
        {
            '$title': 'StageWar live!',
            '$persons': 'www.stagewar.de',
        }
    )

    render('outro.svg',
        '../outro.ts',
        outroFrames
    )

def tasks(queue, args, idlist, skiplist):
    # iterate over all events extracted from the schedule.xml export
    for event in events(scheduleUrl):
        if event['room'] not in ('Sondermaschinenbau'):
            print("skipping room %s (%s [%s])" % (event['room'], event['title'], event['id']))
            continue
        if not (idlist==[]):
            if 000000 in idlist:
                print("skipping id (%s [%s])" % (event['title'], event['id']))
                continue
            if int(event['id']) not in idlist:
                print("skipping id (%s [%s])" % (event['title'], event['id']))
                continue

        # generate task descriptions and put them into the queue
        queue.put(Rendertask(
            infile = 'intro.svg',
            outfile = str(event['id'])+".ts",
            sequence = introFrames,
            parameters = {
                '$title': event['title'],
                '$persons': event['personnames']
            }
        ))

    # place a task for the outro into the queue
    if not "out" in skiplist:
        queue.put(Rendertask(
            infile = 'outro.svg',
            outfile = 'outro.ts',
            sequence = outroFrames
        ))
