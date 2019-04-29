database_config = {
    'foosbot_dev':{
        'driver': 'sqlite',
        'database':'/home/proth/Documents/code/foosbot/foosbot/foos.db',
    },
    'foosbot':{
        'driver': 'mysql',
        'host':'Aurelion.mysql.pythonanywhere-services.com',
        'username':'Aurelion',
        'password':'proth314',
        'database':'Aurelion$foosbot',
    }
}

# convenience function for creating a db connection
def connection(name):
    return Connection(name)

# convenience function for creating a db query builder object
def builder(name):
    return Builder(name)

def schema(name):
    return DBSchema(name)

def get_ssl(config):
    if 'ssl' not in config: return None

    import os.path as path
    if path.isfile(config.get('ssl',{}).get('ca')): return config['ssl']
    
    from credentials import ssl_alternatives
    for row in ssl_alternatives:
        if path.isfile(row.get('ca')): return row

def get_local_name(name):
    pass
    #If running on local, return dev version of connection string
    
        
# This class creates and maintains database connections. 
# Simply initialize it with connection name and a connection object will be returned
class Connection:
    connections = {}

    def __new__(self, name):
        #If we've already made this connection, return the existing one.
        if name in Connection.connections:
            return Connection.connections[name]
        else:
            #Make sure this connection has a configuration
            if name not in database_config: 
                raise Exception('Database connection not configured: '+name)
            
            #load and connect
            import pymysql
            config = database_config[name]
            Connection.connections[name] = conn = pymysql.connect(
                host=config['host'], 
                user=config['user'], 
                password=config['password'],
                database=config['database'], 
                port=config.get('port', None),
                ssl=get_ssl(config)
                )
            
            return conn

# This class creates and maintains orator DatabaseManager objects. These are the base object for query building with Laravel style syntax.
class Builder:
    connections = {}
    
    def __new__(self, name):
        #If we've already made this connection, return the existing one.
        if name in Builder.connections:
            return Builder.connections[name]
        else:
            #Make sure this connection has a configuration
            if name not in database_config: 
                raise Exception('Database connection not configured: '+name)
            
            from orator import DatabaseManager
            #load and connect
            config = {'default': dict(database_config[name])}
            config['default']['driver'] = config['default'].get('driver', 'mysql')
            if 'ssl' in config['default']: config['default']['ssl'] = get_ssl(config['default'])

            Builder.connections[name] = db = DatabaseManager(config)
            
            return db

class DBSchema:
    connections = {}
    
    def __new__(self, name):
        #If we've already made this connection, return the existing one.
        if name in DBSchema.connections:
            return DBSchema.connections[name]
        else:
            #Make sure this connection has a configuration
            if name not in database_config: 
                raise Exception('Database connection not configured: '+name)
            
            from orator import Schema

            db = builder(name)
            schema = Schema(db)
            DBSchema.connections[name] = dbschema = schema.connection('default')
            
            return dbschema


if __name__ == '__main__':
    db = connection('datastore')
    print(db.table('accounts').limit(1).first())
    
