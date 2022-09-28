db.createUser({ user:"mongousr", pwd:"mongopwd", roles: [ "readWrite" ] });
db.createUser({ user:"admin", pwd:"mongopwd", roles: [ "dbAdmin", "readWrite" ] });

db = db.getSiblingDB('comic-back');
db.createCollection('comics')