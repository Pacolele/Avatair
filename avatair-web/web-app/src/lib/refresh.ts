import { PUBLIC_BACKEND_API_URL } from "$env/static/public";
import { getCookie } from "./cookie";

export async function refreshTokens() {
    const response = await fetch(`${PUBLIC_BACKEND_API_URL}/auth/refresh`, {
        method: "GET",
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${getCookie("refresh_token")}`,
        },
    });

    // Access token expired
    if (response.status == 401) {
        window.location.replace("/?logged-out");
        return;
    }

    // Return cookies
    return response.json();
}