from renderlib import *
from easing import *

# URL to Schedule-XML
scheduleUrl = 'https://cfp.fairydust.reisen/iger-2023/schedule/export/schedule.xml'

def rocket(frame, frames=10*fps, start=-90):
    ox = 960
    oy = 1807

    a = frame*360/frames

    return (
        ('Uboot', 'attr', 'transform', f'rotate({start+a} {ox} {oy})'),
        *(
            (f'orbit{j:02}', 'attr', 'transform', f'scale({min(max(0, 1-(abs(-start+90-a-(28-j)*360/69)-5)/30), 1)})')
            for j in range(1, 21)
        ),
    )

def introFrames(args):
    for i in range(5*fps):
        yield (
            ('title', 'style', 'opacity', easeInQuad(min(i, fps), 0, 1, fps)),
            ('persons', 'style', 'opacity', easeInQuad(min(i, fps), 0, 1, fps)),
            *rocket(i),
        )

def outroFrames(args):
    for i in range(5*fps):
        yield (
            ('license', 'style', 'opacity', easeInQuad(min(i, fps), 0, 1, fps)),
            ('voc', 'style', 'opacity', easeInQuad(min(i, fps), 0, 1, fps)),
            *rocket(i),
        )

def pauseFrames(args):
    for i in range(10*fps):
        yield rocket(i)

def debug():
    render('intro.svg',
        '../intro.ts',
        introFrames,
        {
            '$id': 2342,
            '$title': 'Varus live!',
            '$subtitle': 'Metal Konzert',
            '$persons':  'varus-band.de',
        }
    )

    render('outro.svg',
        '../outro.ts',
        outroFrames
    )

    render('pause.svg',
        '../pause.ts',
        pauseFrames
    )

def tasks(queue, args, idlist, skiplist):
    # iterate over all events extracted from the schedule xml-export
    for event in events(scheduleUrl):
        if "in" in skiplist:
            break

        if event['room'] not in ('Vortragsraum'):
            print("skipping room %s (%s [%s])" % (event['room'], event['title'], event['id']))
            continue
        if not event['record']:
            print("skipping %s [%s] (do not record)" % (event['title'], event['id']))
            continue
        if not (idlist==[]):
            if 000000 in idlist:
                print("skipping id (%s [%s])" % (event['title'], event['id']))
                continue
            if int(event['id']) not in idlist:
                print("skipping id (%s [%s])" % (event['title'], event['id']))
                continue

        # generate a task description and put them into the queue
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

    # place the pause-sequence into the queue
    if not "pause" in skiplist:
        queue.put(Rendertask(
            infile = 'pause.svg',
            outfile = 'pause.ts',
            sequence = pauseFrames
        ))
