const decoder = require('./lib/open-replay-decoder.js');

function bsor_to_xror(raw) {
  const bsor = decoder.decode(raw);
  return {
    "$schema": "https://metaguard.github.io/xror/schema/v0.1.0/schema.json",
    "info": {
      "timestamp": parseInt(bsor.info.timestamp),
      "hardware": {
        "devices": [
          { "name": bsor.info.hmd, "type": "HMD", "joint": "HEAD", "axes": ["x","y","z","i","j","k","1"] },
          { "name": bsor.info.controller.replaceAll('Right', 'Left').replaceAll('right', 'left'), "type": "CONTROLLER", "joint": "HAND_LEFT", "axes": ["x","y","z","i","j","k","1"] },
          { "name": bsor.info.controller, "type": "CONTROLLER", "joint": "HAND_RIGHT", "axes": ["x","y","z","i","j","k","1"] }
        ]
      },
      "software": {
        "api": bsor.info.trackingSystem,
        "runtime": bsor.info.platform,
        "app": {
          "version": bsor.info.gameVersion,
          "extensions": [
            {
              "version": bsor.info.version
            }
          ]
        },
        "environment": {
          "name": bsor.info.environment
        },
        "activity": {
          id: bsor.info.hash,
          name: bsor.info.songName,
          mapper: bsor.info.mapper,
          difficulty: bsor.info.difficulty,
          score: bsor.info.score,
          mode: bsor.info.mode,
          modifiers: bsor.info.modifiers,
          jumpDistance: bsor.info.jumpDistance,
          leftHanded: bsor.info.leftHanded,
          height: bsor.info.height,
          startTime: bsor.info.startTime,
          failTime: bsor.info.failTime,
          speed: bsor.info.Speed
        }
      },
      "user": {
        "id": bsor.info.playerID,
        "name": bsor.info.playerName
      }
    },
    "frames": bsor.frames.map(frame => [frame.time, frame.h.p.x, frame.h.p.y, frame.h.p.z, frame.h.r.x, frame.h.r.y, frame.h.r.z, frame.h.r.w, frame.l.p.x, frame.l.p.y, frame.l.p.z, frame.l.r.x, frame.l.r.y, frame.l.r.z, frame.l.r.w, frame.r.p.x, frame.r.p.y, frame.r.p.z, frame.r.r.x, frame.r.r.y, frame.r.r.z, frame.r.r.w]),
    "events": [
      {
        "name": "note",
        "attr": ["noteID", "eventTime", "spawnTime", "eventType", "speedOK", "directionOK", "saberTypeOK", "wasCutTooSoon", "saberSpeed", "saberDir", "saberType", "timeDeviation", "cutDirDeviation", "cutPoint", "cutNormal", "cutDistanceToCenter", "cutAngle", "beforeCutRating", "afterCutRating"],
        "instances": bsor.notes.map(note => note.noteCutInfo ? [note.noteID, note.eventTime, note.spawnTime, note.eventType, note.noteCutInfo.speedOK, note.noteCutInfo.directionOK, note.noteCutInfo.saberTypeOK, note.noteCutInfo.wasCutTooSoon, note.noteCutInfo.saberSpeed, note.noteCutInfo.saberDir, note.noteCutInfo.saberType, note.noteCutInfo.timeDeviation, note.noteCutInfo.cutDirDeviation, note.noteCutInfo.cutPoint, note.noteCutInfo.cutNormal, note.noteCutInfo.cutDistanceToCenter, note.noteCutInfo.cutAngle, note.noteCutInfo.beforeCutRating, note.noteCutInfo.afterCutRating ] : [note.noteID, note.eventTime, note.spawnTime, note.eventType ])
      },
      {
        "name": "wall",
        "attr": ["wallID", "energy", "spawnTime"],
        "instances": bsor.walls.map(wall => [wall.wallID, wall.energy, wall.spawnTime])
      },
      {
        "name": "height",
        "attr": ["height"],
        "instances": bsor.heights.map(height => [height.height])
      },
      {
        "name": "pause",
        "attr": ["duration"],
        "instances": bsor.pauses.map(pause => [pause.duration])
      }
    ]
  }
}

module.exports = bsor_to_xror;
