<script>
    import { PUBLIC_BACKEND_API_URL} from '$env/static/public';
    import { getCookie, setCookie, removeCookie } from "$lib/cookie";
    import { refreshTokens } from '$lib/refresh';

    // TODO just delete local cookie and redirect to /
    function logout() {
        fetch(`${PUBLIC_BACKEND_API_URL}/auth/logout`, {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${getCookie("access_token")}`,
            },
        })
            .then(async (response) => {
                // Token expired
                if (response.status == 401) {
                    const tokens = await refreshTokens();

                    // Save tokens as cookies
                    setCookie("access_token", tokens["accessToken"]);
                    setCookie("refresh_token", tokens["refreshToken"]);

                    // Try again
                    return logout();
                }

                // Unexpected error
                if (response.status != 200) return;

                // Delete cookies
                removeCookie("access_token");
                removeCookie("refresh_token");

                // Redirect to login page
                window.location.replace("/");
            })
            .catch((error) => {
                console.error(error);
            });
    }
</script>

<header>
    <h1>AVATAR AIR</h1>
    <div class="clouds">
            <div class="cloud" style="padding: 50px;right: -15px;top: -50px;"></div>
            <div class="cloud" style="padding: 30px;right: -10px;top: 30px;"></div>
            <div class="cloud" style="padding: 60px;right: -25px;top: 70px;"></div>
            <div style="opacity: 0.6">
                <div class="cloud" style="padding: 80px;right: -30px;top: -110px;"></div>
                <div class="cloud" style="padding: 50px;right: -20px;top: 0px;"></div>
                <div class="cloud" style="padding: 110px;right: -70px;top: 60px;"></div>
            </div>
    </div>
    <div>
        <button class="button button-purple" on:click={logout}>Log Out</button>
        <button class="button button-purple" on:click={logout} id="responsive-icon"><span class="material-symbols-outlined">logout</span></button>
    </div>
</header>


<style>
    @import "/static/css/header.css";
    @import "/static/css/button.css";
    @import "/static/css/clouds.css";
    @import "/static/css/fonts.css";
    /* @import "/static/css/nullify.css"; */
</style>

<slot />