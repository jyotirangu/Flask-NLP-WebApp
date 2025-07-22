import json

class Database: 
    
    def insert(self,name,email,password):
        with open('user.json','r') as rf:
            users = json.load(rf)
            
            if email in users:
                return 0
            else:
                users[email] = [name,password]
                
        with open('user.json', 'w') as wf:
            json.dump(users,wf,indent=4)
            return 1
        
    def search(self,email,password):
        with open('user.json','r') as rf:
            users = json.load(rf)
            
            if email in users:
                if users[email][1] == password:
                    return 1
                else:
                    return 0
                
            else:
                return 0
            
            
            
            # In a statement issued with France and UN chief Antonio Guterres on Saturday, China committed to '"update" its climate target "in a manner representing a progression beyond the current one". It also vowed to publish a long term decarbonisation strategy by next year.
            