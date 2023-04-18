import numpy as np
import fpzip
import bson
import time
import datetime
from bsor.Bsor import make_bsor
from copy import deepcopy

class XROR:
    def __init__(self, id = None, name = None, timestamp = None):
        self.data = {
            "$schema": "https://metaguard.github.io/xror/schema/v1.0.0/schema.json"
        }
        if (id): self.data['$id'] = id
        self.data['info'] = {}
        if (name): self.info['name'] = str(name)
        if (timestamp): self.data['info']['timestamp'] = int(timestamp)
        self.data['info']['hardware'] = {}
        self.data['info']['hardware']['devices'] = []
        self.data['frames'] = []
        self.data['events'] = []

    def __repr__(self):
        return repr(self.data)

    def addDevice(self, name = None, type = None, joint = None, axes = ['x', 'y', 'z', 'i', 'j', 'k', '1'], offsets = None):
        device = {}
        if (name): device['name'] = name
        if (type): device['type'] = type
        if (joint): device['joint'] = joint
        device['axes'] = axes
        if (offsets): device['offsets'] = offsets
        self.data['info']['hardware']['devices'].append(device)

    def setApp(self, id = None, name = None, version = None):
        if ('software' not in self.data['info']): self.data['info']['software'] = {}
        app = {}
        if (id): app['id'] = id
        if (name): app['name'] = name
        if (version): app['version'] = version
        self.data['info']['software']['app'] = app

    def addExtension(self, id = None, name = None, version = None):
        if ('software' not in self.data['info']): self.data['info']['software'] = {}
        if ('app' not in self.data['info']['software']): self.data['info']['software']['app'] = {}
        if ('extensions' not in self.data['info']['software']['app']): self.data['info']['software']['app']['extensions'] = []

        mod = {}
        if (id): mod['id'] = id
        if (name): mod['name'] = name
        if (version): mod['version'] = version
        self.data['info']['software']['app']['extensions'].append(mod)

    def setEnvironment(self, id = None, name = None):
        if ('software' not in self.data['info']): self.data['info']['software'] = {}
        env = {}
        if (id): env['id'] = id
        if (name): env['name'] = name
        self.data['info']['software']['environment'] = env

    def setActivity(self, id = None, name = None):
        if ('software' not in self.data['info']): self.data['info']['software'] = {}
        act = {}
        if (id): act['id'] = id
        if (name): act['name'] = name
        self.data['info']['software']['activity'] = act

    def setUser(self, id = None, name = None):
        usr = {}
        if (id): usr['id'] = id
        if (name): usr['name'] = name
        self.data['info']['user'] = usr

    def addFrame(self, time, data):
        self.data['frames'].append([time] + data)

    def addEventType(self, id = None, name = None, attr = None, floatData = None, otherData = None):
        if ('events' not in self.data): self.data['events'] = []
        ev = {}
        if (id): ev['id'] = id
        if (name): ev['name'] = name
        if (attr): ev['attr'] = attr
        if (floatData): ev['floatData'] = floatData
        if (otherData): ev['otherData'] = otherData
        self.data['events'].append(ev)

    def addEvent(self, type, time, floatData = [], otherData = None):
        idx = None;
        for i in range(len(self.data['events'])):
            if (self.data['events'][i]['id'] == type): idx = i
        if ('floatData' not in self.data['events'][idx]): self.data['events'][idx]['floatData'] = []
        self.data['events'][idx]['floatData'].append([time] + floatData)
        if (otherData):
            if ('otherData' not in self.data['events'][idx]): self.data['events'][idx]['otherData'] = []
            self.data['events'][idx]['otherData'].append(otherData)

    def getEvents(self, type):
        idx = None;
        for i in range(len(self.data['events'])):
            if (self.data['events'][i]['id'] == type): idx = i
        if (idx == None): return None
        events = []
        if ('floatData' not in self.data['events'][idx]): return []
        keys = ['time'] + self.data['events'][idx]['attr']
        for i in range(len(self.data['events'][idx]['floatData'])):
            event = {}
            for j in range(len(self.data['events'][idx]['floatData'][i])):
                event[keys[j]] = self.data['events'][idx]['floatData'][i][j]
            if 'otherData' in self.data['events'][idx]:
                for k in range(len(self.data['events'][idx]['otherData'][i])):
                    event[keys[j+k+1]] = self.data['events'][idx]['otherData'][i][k]
            events.append(event)
        return events

    def pack(self):
        data = deepcopy(self.data)

        if ('timestamp' in data['info']): data['info']['timestamp'] = datetime.datetime.fromtimestamp(data['info']['timestamp'], datetime.timezone.utc)

        frames = np.array(data['frames'], dtype=np.float32)
        bytes = fpzip.compress(frames)
        data['frames'] = bson.binary.Binary(bytes)

        for i in range(len(data['events'])):
            if ('floatData' in data['events'][i]):
                floats = np.array(data['events'][i]['floatData'], dtype=np.float32)
                bytes = fpzip.compress(floats)
                data['events'][i]['floatData'] = bson.binary.Binary(bytes)

        return bson.encode(data)

    def toBSOR(self):
        bytes = bytearray()
        def addInt(int):
            bytes.extend(int.to_bytes(4, 'little'));

        def addFloat(float):
            bytes.extend(np.array([float], dtype=np.float32).tobytes());

        def addByte(byte):
            bytes.extend(byte.to_bytes(1, 'little'))

        def addString(str):
            addInt(len(str))
            bytes.extend(str.encode('utf-8'))

        # Info Structure
        addInt(0x442d3d69)
        addByte(1)
        addByte(0)
        addString(self.data['info']['software']['app']['extensions'][0]['version'])
        addString(self.data['info']['software']['app']['version'])
        addString(str(self.data['info']['timestamp']))
        addString(self.data['info']['user']['id'])
        addString(self.data['info']['user']['name'])
        addString(self.data['info']['software']['api'])
        addString(self.data['info']['software']['runtime'])
        addString(self.data['info']['hardware']['devices'][0]['name'])
        addString(self.data['info']['hardware']['devices'][2]['name'])
        for attr in ['songHash', 'name', 'mapper', 'difficulty']:
            addString(self.data['info']['software']['activity'][attr])
        addInt(self.data['info']['software']['activity']['score'])
        addString(self.data['info']['software']['activity']['mode'])
        addString(self.data['info']['software']['environment']['name'])
        if ('modifiers' in self.data['info']['software']['activity']): addString(self.data['info']['software']['activity']['modifiers'])
        else: addString("")
        addFloat(self.data['info']['software']['activity']['jumpDistance'])
        if ('leftHanded' in self.data['info']['software']['activity']): addByte(self.data['info']['software']['activity']['leftHanded'])
        else: addByte(False)

        for attr in ['height', 'startTime', 'failTime', 'speed']:
            if (attr in self.data['info']['software']['activity']): addFloat(self.data['info']['software']['activity'][attr])
            else: addFloat(0)

        # Frames Array
        addByte(1)
        addInt(len(self.data['frames']))
        fps = self.getEvents('f')
        for i in range(len(self.data['frames'])):
            frame = self.data['frames'][i]
            addFloat(frame[0])
            if fps: addInt(int(fps[i]['fps']))
            else: addInt(0)
            for j in range(1, 22):
                addFloat(frame[j])

        # Notes Array
        addByte(2)
        notes = []
        gc = self.getEvents('gc')
        for c in gc:
            c['eventType'] = 0
            c['speedOK'] = True
            c['directionOK'] = True
            c['saberTypeOK'] = True
            c['saberType'] = (c['noteID'] // 10) % 10
            c['wasCutTooSoon'] = False
        bc = self.getEvents('bc')
        for c in bc:
            c['eventType'] = 1
            c['saberType'] = (c['noteID'] // 10) % 10
            if (not c['saberTypeOK']):
                if c['saberType'] == 0: c['saberType'] = 1
                else: c['saberType'] = 0
        m = self.getEvents('m')
        for c in m:
            c['eventType'] = 2
        b = self.getEvents('b')
        for c in b:
            c['eventType'] = 3
        notes = sum([gc, bc, m, b], [])
        notes = sorted(notes, key=lambda d: d['time'])
        addInt(len(notes))
        for note in notes:
            addInt(note['noteID'])
            addFloat(note['time'])
            addFloat(note['spawnTime'])
            addInt(note['eventType'])
            if (note['eventType'] == 0 or note['eventType'] == 1):
                for attr in ['speedOK', 'directionOK', 'saberTypeOK', 'wasCutTooSoon']: addByte(note[attr])
                for attr in ['saberSpeed', 'saberDirX', 'saberDirY', 'saberDirZ']: addFloat(note[attr])
                addInt(note['saberType'])
                for attr in ['timeDeviation', 'cutDirDeviation', 'cutPointX', 'cutPointY', 'cutPointZ', 'cutNormalX', 'cutNormalY', 'cutNormalZ', 'cutDistanceToCenter', 'cutAngle', 'beforeCutRating', 'afterCutRating']: addFloat(note[attr])

        # Walls Array
        addByte(3)
        walls = self.getEvents('wh')
        addInt(len(walls))
        for wall in walls:
            addInt(wall['wallID'])
            addFloat(wall['energy'])
            addFloat(wall['time'])
            addFloat(wall['spawnTime'])

        # Height Array
        addByte(4)
        heights = self.getEvents('h')
        addInt(len(heights))
        for height in heights:
            addFloat(height['height'])
            addFloat(height['time'])

        # Pause Array
        addByte(5)
        pauses = self.getEvents('p')
        addInt(len(pauses))
        for pause in pauses:
            addFloat(pause['duration'])
            addFloat(pause['time'])

        return bytes

    @classmethod
    def unpack(XROR, file):
        xror = XROR()
        data = bson.decode(file)

        if ('timestamp' in data['info']):data['info']['timestamp'] = int(data['info']['timestamp'].replace(tzinfo=datetime.timezone.utc).timestamp())

        floats = fpzip.decompress(data['frames'])
        data['frames'] = floats[0][0].tolist()

        for i in range(len(data['events'])):
            if ('floatData' in data['events'][i]):
                floats = fpzip.decompress(data['events'][i]['floatData'])
                data['events'][i]['floatData'] = floats[0][0].tolist()

        xror.data = data
        return xror

    @classmethod
    def fromBSOR(XROR, data, addFPS = False):
        bsor = make_bsor(data)
        xror = XROR(timestamp = bsor.info.timestamp)

        xror.addDevice(name = bsor.info.hmd, type = 'HMD', joint = 'HEAD')
        xror.addDevice(name = bsor.info.controller.replace("right", "left").replace("Right", "Left").replace("RIGHT", "LEFT"), type = 'CONTROLLER', joint = 'HAND_LEFT')
        xror.addDevice(name = bsor.info.controller, type = 'CONTROLLER', joint = 'HAND_RIGHT')

        xror.setApp(id = '620980', name = 'Beat Saber', version = bsor.info.gameVersion)
        xror.addExtension(name = 'BeatLeader', version = bsor.info.version)
        xror.setEnvironment(name = bsor.info.environment)
        xror.setActivity(name = bsor.info.songName)
        xror.setUser(id = bsor.info.playerId, name = bsor.info.playerName)
        for attr in ['songHash', 'mapper', 'difficulty', 'score', 'mode', 'modifiers', 'jumpDistance', 'leftHanded', 'height', 'startTime', 'failTime', 'speed']:
            if (getattr(bsor.info, attr)): xror.data['info']['software']['activity'][attr] = getattr(bsor.info, attr)
        xror.data['info']['software']['runtime'] = bsor.info.trackingSystem
        xror.data['info']['software']['api'] = bsor.info.platform

        for frame in bsor.frames:
            data = []
            for obj in ['head', 'left_hand', 'right_hand']:
                for axis in ['x', 'y', 'z', 'x_rot', 'y_rot', 'z_rot', 'w_rot']:
                    data.append(getattr(getattr(frame, obj), axis))
            xror.addFrame(frame.time, data)

        xror.addEventType(id = 'gc', name = 'Good Cut', attr = ['spawnTime', 'saberSpeed', 'saberDirX', 'saberDirY', 'saberDirZ', 'timeDeviation', 'cutDirDeviation', 'cutPointX', 'cutPointY', 'cutPointZ', 'cutNormalX', 'cutNormalY', 'cutNormalZ', 'cutDistanceToCenter', 'cutAngle', 'beforeCutRating', 'afterCutRating', 'noteID']);
        xror.addEventType(id = 'bc', name = 'Bad Cut', attr = ['spawnTime', 'saberSpeed', 'saberDirX', 'saberDirY', 'saberDirZ', 'timeDeviation', 'cutDirDeviation', 'cutPointX', 'cutPointY', 'cutPointZ', 'cutNormalX', 'cutNormalY', 'cutNormalZ', 'cutDistanceToCenter', 'cutAngle', 'beforeCutRating', 'afterCutRating', 'noteID', 'speedOK', 'directionOK', 'saberTypeOK', 'wasCutTooSoon']);
        xror.addEventType(id = 'm', name = 'Miss', attr = ['spawnTime', 'noteID']);
        xror.addEventType(id = 'b', name = 'Bomb Cut', attr = ['spawnTime', 'noteID']);

        for note in bsor.notes:
            if note.event_type == 0:
                xror.addEvent('gc', note.event_time, [note.spawn_time, note.cut.saberSpeed, note.cut.saberDirection[0], note.cut.saberDirection[1], note.cut.saberDirection[2], note.cut.timeDeviation, note.cut.cutDeviation, note.cut.cutPoint[0], note.cut.cutPoint[1], note.cut.cutPoint[2], note.cut.cutNormal[0], note.cut.cutNormal[1], note.cut.cutNormal[2], note.cut.cutDistanceToCenter, note.cut.cutAngle], [note.cut.beforeCutRating, note.cut.afterCutRating, note.note_id])
            if note.event_type == 1:
                xror.addEvent('bc', note.event_time, [note.spawn_time, note.cut.saberSpeed, note.cut.saberDirection[0], note.cut.saberDirection[1], note.cut.saberDirection[2], note.cut.timeDeviation, note.cut.cutDeviation, note.cut.cutPoint[0], note.cut.cutPoint[1], note.cut.cutPoint[2], note.cut.cutNormal[0], note.cut.cutNormal[1], note.cut.cutNormal[2], note.cut.cutDistanceToCenter, note.cut.cutAngle], [note.cut.beforeCutRating, note.cut.afterCutRating, note.note_id, note.cut.speedOK, note.cut.directionOk, note.cut.saberTypeOk, note.cut.wasCutTooSoon])
            if note.event_type == 2:
                xror.addEvent('m', note.event_time, [note.spawn_time], [note.note_id])
            if note.event_type == 3:
                xror.addEvent('b', note.event_time, [note.spawn_time], [note.note_id])

        xror.addEventType(id = 'wh', name = 'Wall Hit', attr = ['energy', 'spawnTime', 'wallID'])
        for wall in bsor.walls:
            xror.addEvent('wh', wall.time, [wall.energy, wall.spawnTime, wall.id])

        xror.addEventType(id = 'h', name = 'Height Change', attr = ['height'])
        for height in bsor.heights:
            xror.addEvent('h', height.time, [height.height])

        xror.addEventType(id = 'p', name = 'Pause', attr = ['duration'])
        for pause in bsor.pauses:
            xror.addEvent('h', pause.time, otherData=[pause.duration])

        if (addFPS):
            xror.addEventType(id = 'f', name = 'FPS', attr = ['fps'])
            for frame in bsor.frames:
                xror.addEvent('f', frame.time, [frame.fps])

        # todo: bomb misses
        # todo: wall misses
        # todo: more user data

        return xror
