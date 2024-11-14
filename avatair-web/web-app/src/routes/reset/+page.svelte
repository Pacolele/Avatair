<script lang="ts">

import { api } from "$lib/API";

let email = '';
let isValidEmail = false;
let errorMessage = '';

function handleEmailInput(event) {
  email = event.target.value;
  isValidEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  
}

async function postRequestResetPassword() {
    console.log("trying to reset the password.....")
    console.log("Email for password reset:", email);
    if (!isValidEmail) {
      console.error('Invalid email address');
      errorMessage = isValidEmail ? '' : 'Please enter a valid email address';
      return; 
    }

    try {
      const response = await api.fetch(
        "auth/reset",
        "post",
        {"Content-Type": "application/json",},
        {email: email}
      )

      if (response.status != 201) {
        throw new Error('Failed to reset password');
      }

      console.log("Password reset request sent successfully");

    } catch (error) {
      console.error('Error resetting password:');

    }
  }

</script>
<div class="gradient-element">
    <div class="clouds">
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
        <h1>Password Reset</h1>
        <div id="form">
            <label for="email">E-mail Adress</label>
            <input type="email" id="email" name="email" placeholder="Enter your e-mail" on:input={handleEmailInput}>
            <div class="error-message">{errorMessage}</div>
            <div class="buttons-element">
                <a href="../" class="button button-grey">Back to login</a>
                <a href="" class="button button-purple"on:click|preventDefault={postRequestResetPassword}>Reset password</a>
            </div>
        </div>
    </div>
    <div class="clouds">
        <div class="slide-right slide-1">
            <div class="cloud" style="padding: 15vh; left: -5vh; top: -10vh"></div>
            <div class="cloud" style="padding: 10vh; left: -5vh; top: 15vh"></div>
            <div class="cloud" style="padding: 12vh; left: -15vh; top: 30vh"></div>
            <div class="cloud" style="padding: 15vh; left: -25vh; top: 40vh"></div>
            <div class="cloud" style="padding: 10vh; left: -10vh; top: 55vh"></div>
            <div class="cloud" style="padding: 10vh; left: -5vh; top: 70vh"></div>
            <div class="cloud" style="padding: 20vh; left: -5vh; top: 80vh"></div>
        </div>
        <div class="slide-right slide-2" style="opacity: 0.7;">
            <div class="cloud" style="padding: 20vh; left: 5vh; top: -20vh"></div>
            <div class="cloud" style="padding: 20vh; left: -15vh; top: 5vh"></div>
            <div class="cloud" style="padding: 15vh; left: -10vh; top: 40vh"></div>
            <div class="cloud" style="padding: 20vh; left: -5vh; top: 65vh"></div>
            <div class="cloud" style="padding: 30vh; left: 0vh; top: 80vh"></div>
        </div>
        <div class="slide-right slide-3" style="opacity: 0.4;">
            <div class="cloud" style="padding: 30vh; left: -5vh; top: -35vh"></div>
            <div class="cloud" style="padding: 20vh; left: -10vh; top: 5vh"></div>
            <div class="cloud" style="padding: 10vh; left: 10vh; top: 35vh"></div>
            <div class="cloud" style="padding: 30vh; left: -20vh; top: 45vh"></div>
            <div class="cloud" style="padding: 40vh; left: -10vh; top: 70vh"></div>
        </div>
    </div>
</div>

<style>
    @import "/static/css/login.css";
    @import "/static/css/fonts.css";
    @import "/static/css/clouds.css";
    @import "/static/css/button.css";
</style>