import {describe, expect, it} from 'vitest';
import { api, UserNamePasswordRegStrategy } from "../lib/API"
import { PUBLIC_BACKEND_API_URL, PUBLIC_FRONTEND_URL } from '$env/static/public';

describe("API auth", async () => {
    it("should create a new user admin@philipphock.rocks and asd",async ()=>{        
        
        const res  = await api.register(new UserNamePasswordRegStrategy("admin@philipphock.rocks", "asd"));
        console.log(res.status); 
           
        expect(res.status).toBe(201);
         
    })
})