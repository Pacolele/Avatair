<script lang="ts">
  import { UserNamePasswordRegStrategy, api } from '$lib/API';
  import { AxiosError } from 'axios';

    let errorText = "";

    let user = {
        email: "",
        password: ""
    };

    let confirmPass = "";

    async function signup() {
        if ([user.email, user.password, confirmPass].some(x => x.length == 0)) {
            errorText = "Please fill in all fields";
            return;
        }

        if (user.password != confirmPass) {
            errorText = "Passwords do not match!"
            return;
        }
        try{
            await api.register(new UserNamePasswordRegStrategy(user.email, user.password));    
            window.location.replace("/");        
        }catch(e){
            if (e instanceof AxiosError){
                console.log(e)
                errorText = e.response?.data?.message;
            }else{
                errorText = "An unexpected error occurred, please try again later.";
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
            <div class="cloud" style="padding: 15vh; right: -5vh; top: -10vh"></div>
            <div class="cloud" style="padding: 10vh; right: -5vh; top: 15vh"></div>
            <div class="cloud" style="padding: 12vh; right: -15vh; top: 30vh"></div>
            <div class="cloud" style="padding: 15vh; right: -25vh; top: 40vh"></div>
            <div class="cloud" style="padding: 10vh; right: -10vh; top: 55vh"></div>
            <div class="cloud" style="padding: 10vh; right: -5vh; top: 70vh"></div>
            <div class="cloud" style="padding: 20vh; right: -5vh; top: 80vh"></div>
        </div>
        <div class="slide-left slide-2" style="opacity: 0.7;">
            <div class="cloud" style="padding: 20vh; right: 5vh; top: -20vh"></div>
            <div class="cloud" style="padding: 20vh; right: -15vh; top: 5vh"></div>
            <div class="cloud" style="padding: 15vh; right: -10vh; top: 40vh"></div>
            <div class="cloud" style="padding: 20vh; right: -5vh; top: 65vh"></div>
            <div class="cloud" style="padding: 30vh; right: 0vh; top: 80vh"></div>
        </div>
        <div class="slide-left slide-3" style="opacity: 0.4;">
            <div class="cloud" style="padding: 30vh; right: -5vh; top: -35vh"></div>
            <div class="cloud" style="padding: 20vh; right: -10vh; top: 5vh"></div>
            <div class="cloud" style="padding: 10vh; right: 10vh; top: 35vh"></div>
            <div class="cloud" style="padding: 30vh; right: -20vh; top: 45vh"></div>
            <div class="cloud" style="padding: 40vh; right: -10vh; top: 70vh"></div>
        </div>
    </div>
    <div class="login-container">
        <h1>Create an account</h1>
        <div id="form">
            <label for="email">E-mail Adress</label>
            <input type="email" id="email" name="email" bind:value={user.email} placeholder="Enter your e-mail">
            <label for="password">Password</label>
            <input type="password" id="password" name="password" bind:value={user.password} placeholder="Enter your password">
            <label for="confirm-password">Confirm Password</label>
            <input type="password" id="confirm-password" name="confirm-password" bind:value={confirmPass} placeholder="Re-enter your password">
            <p class="error-text">{errorText}</p>
            <!-- svelte-ignore a11y-missing-attribute -->
            <div class="buttons-element">
                <!-- svelte-ignore a11y-click-events-have-key-events -->
                <a on:click={signup} role="button" id="btnSignup" tabindex="-1" class="button button-purple">Sign Up</a>
            </div>
        </div>
        <br>
        <p>Already have an account? <a href="../">Sign in</a></p>
    </div>
</div>

<style>
    @import "/static/css/login.css";
    @import "/static/css/fonts.css";
    @import "/static/css/clouds.css";
    @import "/static/css/button.css";
</style>