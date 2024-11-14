<script lang="ts">
  import Modal from "../Modal.svelte";
  import { PUBLIC_FRONTEND_URL } from "$env/static/public";
  import { getCookie, setCookie } from "$lib/cookie";
  import { onMount } from "svelte";
  import { refreshTokens } from "$lib/refresh";
  import Switch from "./Switch.svelte";
  import { api } from "$lib/API";
  import Fa from 'svelte-fa'
  import { faUser, faStar, faFile,  faClipboard } from '@fortawesome/free-regular-svg-icons'
  import { faSliders, faGear, faGears } from '@fortawesome/free-solid-svg-icons'

  let surveyTitle = "";
  let surveyDescription = "";
  let surveyActivated = false;
  let surveyId: string | null;
  let errorText = "";
  let survey: any;

  let showModal: boolean = false;

  // TODO replace with api/survey call await survey.getSurvey(id)
  async function getSurvey() {
    // api.survey
    await api
      .fetch("survey/" + surveyId, "get", {
        "Content-Type": "application/json",
        Authorization: `Bearer ${getCookie("access_token")}`,
      })
      .then(async (response) => {
        if (response.status != 200) {
          errorText =
            "An unexpected server-error occured, please try again later.";
        } else {
          errorText = "";
          const result = await response.data;
          survey = result;
          surveyTitle = survey.title;
          surveyActivated = survey.activated;
          if ("description" in survey) surveyDescription = survey.description;
          document.querySelector("input[type='checkbox']").checked = surveyActivated;
        }
      })
      .catch((error) => {
        errorText =
          "An unexpected server-error occured, please try again later.";
        console.error(error);
      });
  }

  async function postSurvey() {
    if (surveyTitle != "") {
      const update = {
        title: surveyTitle,
        description: surveyDescription,
        activated: surveyActivated,
      };
      console.log("the new survey status" + surveyActivated)
      await api
        .fetch(
          "survey/edit",
          "patch",
          {
            "Content-Type": "application/json",
            Authorization: `Bearer ${getCookie("access_token")}`,
          },
          { _id: surveyId, updates: update },
        )
        .then(async (response) => {
          if (response.status == 401) {
            const tokens = await refreshTokens();

            // Save tokens as cookies
            setCookie("access_token", tokens["accessToken"]);
            setCookie("refresh_token", tokens["refreshToken"]);

            // Try again
            return postSurvey();
          } else if (response.status != 200) {
            errorText =
              "An unexpected server-error occured, please try again later.";
          }
        })
        .catch((error) => {
          errorText =
            "An unexpected server-error occured, please try again later.";
          console.error("THIS IS THE ERROR", error);
        });
    } else {
      errorText = "The title can't be empty.";
    }
  }

  function copyLink() {
    const textBox = document.querySelector(".link-box input");
    const popUp = document.querySelector(".link-box p");

    popUp.style.opacity = 1;

    // document.querySelector("#link-box::after").style.opacity = 1;

    textBox.select();
    textBox.setSelectionRange(0, 99999); // For mobile devices

    navigator.clipboard.writeText(textBox.value);
  }

  function handleClick(event) {
    surveyActivated = event.target.checked;
    console.log
    console.log("here")
    console.log(surveyActivated)
    postSurvey()

  };

  onMount(() => {
    const urlParams = new URLSearchParams(window.location.search);
    surveyId = urlParams.get("survey");
    getSurvey();

  });
</script>



<div class="container-column">
  <div class="container-row" style="margin-top: 50px">
    <span
      class="survey-name"
      role="textbox"
      aria-multiline="false"
      placeholder="test">{surveyTitle}</span
    >
    <button
      on:click={() => {
        showModal = true;
      }}
      id="survey-settings"
      class="button button-transparent button-icon button-settings"
    >
      <Fa icon={faGear} size="1.5x"/>
    </button>
    <!-- <span class="material-symbols-outlined">edit</span> -->
  </div>
  <!-- <button class="button button-green button-fade" on:click={postTitle} bind:this={saveButton}>Change Title<span class="material-symbols-outlined">edit_square</span></button> -->
  <p class="error-text">{errorText}</p>

  <Switch label="Activate Survey" bind:checked ={surveyActivated} on:click = {handleClick} />
{#if surveyActivated}
  <div class="link-box"> 
    <input
      type="text"
      value="{PUBLIC_FRONTEND_URL}/survey?survey={surveyId}"
      readonly
    />
    <button on:click={copyLink}>
      <Fa icon={faClipboard} size="1.5x"/>
    </button>
    <p>Link Copied!</p>
  </div>
{/if}
</div>
<div id="menu-container">
  <a href="./edit_survey/generative?survey={surveyId}" class="button-edit">
    <Fa icon={faUser} size="3x"/>
    <p class="menu-text">Generative variables</p>
  </a>
  <a href="./edit_survey/rating?survey={surveyId}" class="button-edit">
    <Fa icon={faSliders} size="3x"/>
    <p class="menu-text">Rating scales</p>
  </a>
  <a href="./edit_survey/parameters?survey={surveyId}" class="button-edit">
    <Fa icon={faGears} size="3x"/>
    <p class="menu-text">Survey <br /> parameters</p>
  </a>
  <a href="./edit_survey/pages?survey={surveyId}" class="button-edit">
    <Fa icon={faFile} size="3x"/>
    <p class="menu-text">Pages</p>
  </a>
</div>
<Modal
  bind:showModal
  cancelText="Close"
  doneText="Save"
  doneFunction={() => {
    postSurvey();
    showModal = false;
  }}
>
  <span class="modal__title" slot="header">Survey settings</span>

  <div class="input" slot="content">
    <p>Name</p>
    <input type="text" bind:value={surveyTitle} placeholder="My Survey" />

    <p>Description</p>
    <textarea
      style="height:150px;font-size:15px;width:400px;resize:none"
      bind:value={surveyDescription}
      placeholder="My Survey is about..."
    ></textarea>
  </div>
</Modal>

<style>
  @import "static/css/fonts.css";
  @import "/static/css/edit.css";
  @import "/static/css/modal.css";
  @import "/static/css/header.css";
  @import "/static/css/button.css";
  @import "@fortawesome/fontawesome-free/css/all.min.css";

</style>
