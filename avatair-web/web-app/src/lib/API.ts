import axios, { AxiosError, type AxiosResponse } from "axios";
import { getCookie, setCookie } from "./cookie";
import {
  PUBLIC_BACKEND_API_URL,
  PUBLIC_FRONTEND_URL,
} from "$env/static/public";

class API {
  private authResponseCallback: (response: any) => void = (_) => {};
  constructor(private apiEndpoint: string, private frontend: string) {}

  addAuthResponse(callback: (response: AxiosResponse) => void) {
    this.authResponseCallback = callback;
  }

  async register(strategy: AuthStrategy) {
    const data = strategy.data({});
    const ret = await axios({
      method: "put",
      baseURL: this.apiEndpoint,
      url: strategy.endpoint,
      data: data,
    });
    return ret;
  }
  async login(strategy: AuthStrategy): Promise<AxiosResponse<any, any>> {
    const data = strategy.data({});
    const ret = await axios({
      method: strategy.method,
      baseURL: this.apiEndpoint,
      url: strategy.endpoint,
      data: data,
    });

    if (ret.status === 200) {
      setCookie("access_token", ret.data["accessToken"]);
      setCookie("refresh_token", ret.data["refreshToken"]);
    }

    this.authResponseCallback(ret);
    return ret;
  }
  async refreshAuth(): Promise<Number> {
    const ret = await axios({
      method: "GET",
      baseURL: this.apiEndpoint,
      url: "auth/refresh",
      headers: {
        Authorization: `Bearer ${getCookie("refresh_token")}`,
      },
    });
    if (ret.status == 401) {
      return 401;
    }
    setCookie("refresh_token", ret.data["refreshToken"]);
    setCookie("access_token", ret.data["accessToken"]);

    return ret.status;
  }

  async fetch(
    endpoint: string,
    method: RequestType = "get",
    headers: Record<string, string> = {},
    body?: any,
    responseType?: any,
  ): Promise<AxiosResponse> {
    try {
      const ret = axios({
        method: method,
        baseURL: this.apiEndpoint,
        url: endpoint,
        responseType: responseType,
        headers: {
          Authorization: `Bearer ${getCookie("access_token")}`,
          ...headers
        },
        data: body,
      });

      return ret;
    } catch (e) {
      if (e instanceof AxiosError) {
        if (e.response?.status) {
          const r2 = await this.refreshAuth();
          if (r2 == 200) {
            return this.fetch(endpoint, method, headers, body, responseType);
          } else {
            throw e;
          }
        } else {
          throw e;
        }
      } else {
        throw e;
      }
    }
  }
}
class Survey{
  constructor(private api: API){}
  
  getSurvey(id: string){
    return this.api.fetch(`survey/${id}`);    
  }
}
type RequestType = "get" | "post" | "put" | "patch" | "delete";

export abstract class AuthStrategy {
  constructor(public readonly method: RequestType, public endpoint: string) {}
  abstract data(data: any): void;
  abstract header(data: any): void;
}

export class UserNamePasswordAuthStrategy extends AuthStrategy {
  constructor(private username: string, private password: string) {
    super("post", "auth/login");
  }

  data(data: any): any {
    return { ...data, username: this.username, password: this.password };
  }
  header(header: any) {
    return header;
  }
}
export class UserNamePasswordRegStrategy extends AuthStrategy {
  constructor(private username: string, private password: string) {
    super("put", "auth/signup");
  }
  data(data: any): any {
    return { ...data, email: this.username, password: this.password };
  }
  header(header: any) {
    return header;
  }
}
export const api = new API(PUBLIC_BACKEND_API_URL, PUBLIC_FRONTEND_URL);
export const survey = new Survey(api);
