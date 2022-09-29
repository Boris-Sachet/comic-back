db = db.getSiblingDB('comic-back');

db.createUser({ user:"mongousr", pwd:"mongopwd", roles: [ { role: "readWrite", db: "comic-back" } ] });
db.createUser({ user:"admin", pwd:"mongopwd", roles: [{ role: "dbAdmin", db: "comic-back" }, { role: "readWrite", db: "comic-back" }] });

db.createCollection('comics');