<script lang="ts">
    import Modal from "../Modal.svelte";
    import { register, type SwiperContainer } from "swiper/element/bundle";
    import { getCookie, setCookie } from "$lib/cookie";
    import { refreshTokens } from "$lib/refresh";
    import { onMount } from "svelte";
    import { api } from "$lib/API";
    import { AxiosError } from "axios";

    let surveyTitle = "";
    let surveyDescription = "";
    let surveyActivated = false;
    let surveyId: string | null;
    let errorText = "";
    let survey: any;
    let allResponses = []
    let nrOfResponses = 0;
    let showModal: boolean = false;

    async function getAllResponses() {


    }

    async function deleteAllResponses() {


    }
    
    async function getSurvey() {
      await api.fetch(
        ("survey/" + surveyId), 
        "post", 
        {
          "Content-Type": "application/json",
          Authorization: `Bearer ${getCookie("access_token")}`,
        }
      )             
      .then(async (response) => {
        if (response.status != 200) {
          errorText =
            "An unexpected server-error occured, please try again later.";
        } else {
          errorText = "";
          survey = await response.data;
          surveyTitle = survey.title;
          surveyActivated = survey.activated;
          if ("description" in survey) surveyDescription = survey.description;
        }
      })
      .catch((error) => {
        errorText =
          "An unexpected server-error occured, please try again later.";
        console.error(error);
      });
      console.log("getting survey....")
      console.log(survey);
  }

  function download_survey() {
    var dlink = document.createElement("a");
    dlink.setAttribute(
      "href",
      "data:application/json," + encodeURIComponent(JSON.stringify(survey))
    );
    dlink.setAttribute("download", surveyTitle);

    dlink.style.display = "none";
    document.body.append(dlink);

    dlink.click();
    dlink.remove();
  }

    onMount(() => {
    const urlParams = new URLSearchParams(window.location.search);
    surveyId = urlParams.get("survey");
    getSurvey();
  });


</script>
<div class="container-column">
    <div class="container-row" style="margin-top: 50px">
        <div class="survey-name-row">
            <span
                class="survey-name"
                role="textbox"
                aria-multiline="false"
                placeholder="test">Survey name: {surveyTitle}</span>
        </div>
        <div class="survey-id-row">
            <span
                class="survey-id"
                role="textbox"
                aria-multiline="false"
                placeholder="test">Survey id: {surveyId}</span>
        </div>
    </div>
    <div class="survey-id-row">
        <span
            class="survey-id"
            role="textbox"
            aria-multiline="false"
            placeholder="test">Number of responses: {nrOfResponses}</span>
    </div>
    <button on:click={download_survey} class="button button-purple">
        Download Survey
        <span class="material-symbols-outlined">download</span>
    </button>
</div>