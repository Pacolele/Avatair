import { browser } from "$app/environment";

export function getCookie(cookieName: string) {

    if (browser) {
        return document.cookie
        .split(";")
        .find((row) => row.trim().startsWith(cookieName + "="))
        ?.split("=")[1];
    }
}

export function setCookie(cookieName: string, cookieValue: string) {
    document.cookie = `${cookieName}=${cookieValue};path=/`;
}

export function removeCookie(cookieName: string) {
    document.cookie = `${cookieName}=;path=/;expires=Thu, 01 Jan 1970 00:00:01 GMT`;
}
