# gaia_tools.query: some helper functions for querying the Gaia database
import time
import numpy
from astropy.table import Table
from astroquery.gaia import Gaia
import psycopg2
from gaia_tools.query import cache as query_cache

def query(sql_query,local=False,timeit=False,use_cache=True,
          dbname='catalogs',user='postgres'):
    """
    NAME:
       query
    PURPOSE:
       perform a query, either on a local server or on the Gaia archive
    INPUT:
       sql_query - the text of the query
       local= (False) if True, run the query on a local postgres database
       timeit= (False) if True, print how long the query ran
       use_cache= (True) if True use the query cache (load from the cache if exists, store to the cache for reuse otherwise)
       dbname= ('catalogs') if local, the name of the postgres database
       user= ('postgres') if local, the name of the postgres user
    OUTPUT:
       result
    HISTORY:
       2018-05-02 - Written - Bovy (UofT)
    """
    if local and 'gaiadr2.' in sql_query:
        sql_query= sql_query.replace('gaiadr2.','gaiadr2_')
    elif not local and 'gdr2_' in sql_query:
        sql_query= sql_query.replace('gaiadr2_','gaiadr2.')
    if use_cache:
        out= query_cache.load(sql_query)
        if out: return out
    if local:
        conn= psycopg2.connect("dbname={} user={}".format(dbname,user))
        cur= conn.cursor()
        if timeit: start= time.time()
        cur.execute(sql_query)
        if timeit: print("Query took {:.3f} s".format(time.time()-start))
        out= cur.fetchall()
        names= [desc[0] for desc in cur.description]
        cur.close()
        conn.close()       
        out= Table(numpy.array(out),names=names)
    else:
        if timeit: start= time.time()
        job= Gaia.launch_job_async(sql_query)
        if timeit: print("Query took {:.3f} s".format(time.time()-start))
        out= job.get_results()
    if use_cache:
        query_cache.save(sql_query,out)
    return out

