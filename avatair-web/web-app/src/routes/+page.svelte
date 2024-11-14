<script lang="ts">
    import { api, UserNamePasswordAuthStrategy } from "$lib/API";
    import { setCookie } from "$lib/cookie";
    import { AxiosError } from "axios";
    import { onMount } from "svelte";

    let errorText = "";

    onMount(() => {
        const urlParams = new URLSearchParams(window.location.search);
        const loggedOut = urlParams.has("logged-out");

        if (loggedOut)
            errorText = "You've been logged out, please log back in.";

        document.addEventListener("keypress", function (event) {
            if (event.key === "Enter") {
                event.preventDefault();
                document?.getElementById("btnLogin")?.click();
            }
        });
    });

    let user = {
        username: null,
        password: null,
    };

    async function login() {
        try {
            const res = await api.login(
                new UserNamePasswordAuthStrategy(
                    user.username ?? "",
                    user.password ?? "",
                ),
            );
            if (res.status == 200) {
                window.location.replace("/account");
            }
        } catch (e) {
            if (e instanceof AxiosError) {
                console.log(e.response);
                errorText =
                    e.response?.data?.message ?? "unexpected error, try later";
            } else {
                errorText = "unexpected error, try later";
            }
        }
    }
</script>

<div class="gradient-element">
    <div class="clouds">
        <div class="title">
            <h1>Welcome to Avatar Air</h1>
            <p>The AI controlled Avatar generator</p>
        </div>
        <div class="slide-left slide-1">
            <div class="cloud" style="padding: 15vh; right: -5vh; top: -10vh" />
            <div class="cloud" style="padding: 10vh; right: -5vh; top: 15vh" />
            <div class="cloud" style="padding: 12vh; right: -15vh; top: 30vh" />
            <div class="cloud" style="padding: 15vh; right: -25vh; top: 40vh" />
            <div class="cloud" style="padding: 10vh; right: -10vh; top: 55vh" />
            <div class="cloud" style="padding: 10vh; right: -5vh; top: 70vh" />
            <div class="cloud" style="padding: 20vh; right: -5vh; top: 80vh" />
        </div>
        <div class="slide-left slide-2" style="opacity: 0.7;">
            <div class="cloud" style="padding: 20vh; right: 5vh; top: -20vh" />
            <div class="cloud" style="padding: 20vh; right: -15vh; top: 5vh" />
            <div class="cloud" style="padding: 15vh; right: -10vh; top: 40vh" />
            <div class="cloud" style="padding: 20vh; right: -5vh; top: 65vh" />
            <div class="cloud" style="padding: 30vh; right: 0vh; top: 80vh" />
        </div>
        <div class="slide-left slide-3" style="opacity: 0.4;">
            <div class="cloud" style="padding: 30vh; right: -5vh; top: -35vh" />
            <div class="cloud" style="padding: 20vh; right: -10vh; top: 5vh" />
            <div class="cloud" style="padding: 10vh; right: 10vh; top: 35vh" />
            <div class="cloud" style="padding: 30vh; right: -20vh; top: 45vh" />
            <div class="cloud" style="padding: 40vh; right: -10vh; top: 70vh" />
        </div>
    </div>
    <div class="login-container">
        <h1>Login</h1>
        <div id="form">
            <label for="email">E-mail Adress</label>
            <input
                type="email"
                id="email"
                name="email"
                bind:value={user.username}
                placeholder="Enter your e-mail"
            />
            <label for="password">Password</label>
            <input
                type="password"
                id="password"
                name="password"
                bind:value={user.password}
                placeholder="Enter your password"
            />
            <a href="/reset">Forgot your password?</a>
            <p class="error-text">{errorText}</p>
            <div class="buttons-element">
                <a href="/reg" class="button button-grey">sign up</a>
                <!-- svelte-ignore a11y-click-events-have-key-events a11y-missing-attribute -->
                <a
                    on:click={login}
                    role="button"
                    tabindex="-1"
                    class="button button-purple"
                    id="btnLogin">Login</a
                >
            </div>
        </div>
    </div>
</div>

<style>
    @import "/static/css/login.css";
    @import "/static/css/fonts.css";
    @import "/static/css/clouds.css";
    @import "/static/css/button.css";
</style>
