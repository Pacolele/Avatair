import {describe, expect, it} from 'vitest';
import { api, UserNamePasswordAuthStrategy } from "../lib/API"

describe("API auth", async () => {
    it("should login with username and password",async ()=>{        
        api.addAuthResponse((r)=>{
            console.log("login response cb");
        });
        const res  = await api.login(new UserNamePasswordAuthStrategy("admin@philipphock.rocks", "asd"));
        console.log(res.status); 
          
        expect(res.status).toBe(200);
        
    })
})