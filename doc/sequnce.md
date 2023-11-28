```mermaid
sequenceDiagram
    participant dev as Developer
    participant user as User

    participant api as MasterAPI
    participant worker as MasterWorker
    participant sql as MasterSQL
    participant m_volume as MasterVolume

    participant el as EdgeNodeEventListener
    participant e_volume as EdgeNodeVolume
    participant edge_node as EdgeNodeNginxWEBServer
    
    participant auth as AuthAPI
    participant dns as DNS

    dev ->>+ api: post multiform zip archive + meta info (path)
    api ->> api: unzip archive 
    // ideally do it in one sql transaction
    loop for each file in archive
        api ->> api: is file exist? 
        alt file exists:
            api ->> api: compare hash 
            alt hash is not equal
                api ->> api: transaction(update file, update sql)
            end
            // *think about hash collision
        else
            api ->> api: transaction(store file, write sql)
        end
    end
    api ->>- dev: 201, some fancy JSON response 
    worker ->>+ sql: select all new added/updated files from last sync
    sql ->>- worker: list of files' metadata
    worker ->> worker: create a zip archive with all files from metadata
    worker ->>+ sql: get all edge nodes
    sql ->> worker: list of edge nodes
    
```

```bash
/dev/server1/
/dev/server2/


src/
- index.html
- styles
- - main.css
- - component.css
```