const fs = require('fs');
const bsor_to_xror = require('./bsor_to_xror');
const { BSON } = require('bson');
const zlib = require('node:zlib');

const bsor = fs.readFileSync('./example.bsor');
const bsor_brotli = zlib.brotliCompressSync(bsor);
const xror_json = bsor_to_xror(bsor.buffer);
const xror_bson = BSON.serialize(xror_json);
const xror_bson_brotli = zlib.brotliCompressSync(xror_bson);

console.log('BSOR Size', "\t\t", bsor.length);
console.log('BSOR/Brotli Size', "\t", bsor_brotli.length);
console.log('XROR JSON Size', "\t\t", JSON.stringify(xror_json).length)
console.log('XROR BSON Size', "\t\t", xror_bson.length)
console.log('XROR BSON/Brotli Size', "\t", xror_bson_brotli.length)
