<script lang="ts">
  import Modal from "./Modal.svelte";
  import {Swiper} from "swiper";
  import { register, type SwiperContainer} from "swiper/element/bundle";
  import { getCookie, setCookie } from "$lib/cookie";
  import { refreshTokens } from "$lib/refresh";
  import { onMount } from "svelte";
  import { api } from "$lib/API";
  import { AxiosError } from "axios";

  // Init swiper
  register();

  let swiperEl: SwiperContainer|undefined;
  let swiperInstance: Swiper | undefined;
  let showModal: boolean = false;
  let errorText: string = "";
  let errorTextModal: string = "";
  let title: string = "";
  let lastEditedID: string = "";

  let newSurvey: any;
  let surveys = [];
  let files: any;

  // Get surveys when page is loaded
  onMount(() => {
    getSurveys();
    
    const urlParams = new URLSearchParams(window.location.search);
    lastEditedID = urlParams.get("survey");
    
  });

  
  // // Swiper nav buttons
  // function prevSlide() {
  //   swiperEl.swiper.slidePrev();
  // }

  // function nextSlide() {
  //   swiperEl.swiper.slideNext();
  // }

  // Create new element using HTML, eg. "<p>New paragraph</p>"
  function createElementFromHTML(htmlString: string) {
    let div = document.createElement("div");
    div.innerHTML = htmlString.trim();
    return div.firstChild;
  }

  
  
  // Get surveys from database and update swiper
  async function getSurveys() {
    try {
      const ret = await api.fetch("survey");
      const result = ret.data;
      surveys = result;

      swiperEl = document.querySelector('swiper-container');
      if (swiperEl) {
        swiperInstance = swiperEl.swiper;
      }
    } catch (e) {
      if (e instanceof AxiosError) {
        if (e.response?.status === 401) {
          //logged out
          window.location.replace("/");
        } else {
          //TODO display unexpected error properly
          console.error(e);
        }
      } else {
        console.error(e);
        //TODO display unexpected error properly
      }

      //errorText = "An unexpected server-error occured, please try again later.";
    }
  }

  async function download_survey(survey_id: string, surveyTitle: string) {
    const response = await api.fetch(
      "survey/download", 
      "post", 
      { "Content-Type": "application/json" },
      { _id: survey_id },
      "blob",
    );

    const zipBlob = response.data;
      // Create a download link for the zip file
      const url = URL.createObjectURL(zipBlob);
      const link = document.createElement("a");
      link.href = url;
      link.download = surveyTitle + ".zip"; // Name of the zip file

      // Trigger the download
      link.click();

      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);  
  }

  // Show survey creation modal
  function showSurveyModal() {
    // swiperEl.swiper.slideTo(0); // Position swiper on 'New Survey' card
    showModal = true; // Show modal
  }

  // Post new survey to database and update swiper
  async function postSurvey() {
    let update;
    if (title != "") {
      update = {
        title: title,
      };
    } else {
      update = newSurvey;
    }
    console.log(update);
    await api
      .fetch(
        "survey/create",
        "post",
        {
        "Content-Type": "application/json",
        Authorization: `Bearer ${getCookie("access_token")}`,
      },
        update,
      )
      .then(async (response) => {
        // Token expired
        if (response.status == 401) {
          const tokens = await refreshTokens();

          // Save tokens as cookies
          setCookie("access_token", tokens["accessToken"]);
          setCookie("refresh_token", tokens["refreshToken"]);

          // Try again
          return postSurvey();
        }

        if (response.status == 201) {
          errorTextModal = "";
          title = "";
          showModal = false;
        } else {
          errorTextModal =
            "An unexpected server-error occured, please try again later.";
          showModal = true;
        }
      })
      .catch((error) => {
        console.error(error);
        errorTextModal =
          "An unexpected server-error occured, please try again later.";
        showModal = true;
      });
    newSurvey = null;
    await getSurveys();
    if (swiperInstance) {
        swiperInstance.update();
        swiperInstance.slideTo(swiperInstance.slides.length - 1);
    }
  }

  // Delete survey from database and update swiper
  async function deleteSurvey(_id: string) {
    if (!confirm("Are you sure you want to delete this Survey?")) return;

    await api
      .fetch(
        "survey/delete",
        "delete",
        {
        "Content-Type": "application/json",
        Authorization: `Bearer ${getCookie("access_token")}`,
      },
        { _id: _id },
      )
      .then(async (response) => {
        // Token expired
        if (response.status == 401) {
          const tokens = await refreshTokens();

          // Save tokens as cookies
          setCookie("access_token", tokens["accessToken"]);
          setCookie("refresh_token", tokens["refreshToken"]);

          // Try again
          return deleteSurvey(_id);
        }

        if (response.status != 200)
          errorText =
            "An unexpected server-error occured, please try again later.";
      })
      .catch((error) => {
        console.error(error);
        errorText =
          "An unexpected server-error occured, please try again later.";
      });

    getSurveys();
    if (swiperInstance) {
      swiperInstance.update();
    }
  }

  async function parseJsonFile(file: Blob) {
    return new Promise((resolve, reject) => {
      const fileReader = new FileReader();
      fileReader.onload = (event) => resolve(JSON.parse(event.target.result));
      fileReader.onerror = (error) => reject(error);
      fileReader.readAsText(file);
    });
  }

  // Function for uploading a survey
  $: if (files) {
    (async () => {
      let update: any = await parseJsonFile(files[0]);

      delete update["_id"];
      delete update["userid"];
      delete update["createdAt"];
      delete update["updatedAt"];

      newSurvey = update;

      await postSurvey();
    })();
  }
</script>

{#if surveys.length === 0}
  <h1 class ="page-title">Get started...</h1>
  <div class="container-swipe">
    <swiper-container
      slider-per-view="3"
      pagination="true"
      css-mode="true"
      navigation="true"
      keyboard="true"
      space-between="50"
    >
      <swiper-slide>
        <div
          tabindex="-1"
          role="button"
          on:keydown={null}
          on:click={showSurveyModal}
          class="add-surveycard survey-card"
        >
          <h2>New Survey</h2>
          <svg
            xmlns="http://www.w3.org/2000/svg"
            height="80"
            viewBox="0 -960 960 960"
            width="80"
            ><path
              d="M440-280h80v-160h160v-80H520v-160h-80v160H280v80h160v160ZM200-120q-33 0-56.5-23.5T120-200v-560q0-33 23.5-56.5T200-840h560q33 0 56.5 23.5T840-760v560q0 33-23.5 56.5T760-120H200Zm0-80h560v-560H200v560Zm0-560v560-560Z"
            />
          </svg>
        </div>
      </swiper-slide>
    </swiper-container>
    </div>
{:else}
  <h1 class="page-title" style="text-align:center;">My Surveys</h1>
  <p class="error-text">{errorText}</p>

  <div class="container-swipe">
    <swiper-container
      slider-per-view="1"
      pagination="true"
      css-mode="true"
      navigation="true"
      keyboard="true"
      space-between="50"
    >
      <swiper-slide>
        <div
          tabindex="-1"
          role="button"
          on:keydown={null}
          on:click={showSurveyModal}
          class="add-surveycard survey-card"
        >
          <h2>New Survey</h2>
          <svg
            xmlns="http://www.w3.org/2000/svg"
            height="80"
            viewBox="0 -960 960 960"
            width="80"
            ><path
              d="M440-280h80v-160h160v-80H520v-160h-80v160H280v80h160v160ZM200-120q-33 0-56.5-23.5T120-200v-560q0-33 23.5-56.5T200-840h560q33 0 56.5 23.5T840-760v560q0 33-23.5 56.5T760-120H200Zm0-80h560v-560H200v560Zm0-560v560-560Z"
            />
          </svg>
        </div>
      </swiper-slide>
      {#each surveys as survey, i (survey._id)}
        <swiper-slide>
          <div class="survey-card">
            <div class="top">
              <div class="banner"></div>
              <h1>{survey.title}</h1>
              {#if survey.description}
                <p class="survey-content">{survey.description}</p>
              {/if}
            </div>
            <div class="bottom">
              <p class="date">
                Created: {new Date(survey.createdAt).toLocaleString()}
              </p>
              <p class="date">
                Updated: {new Date(survey.updatedAt).toLocaleString()}
              </p>
              <div class="buttons">
                <a
                  href={`./account/edit_survey?survey=${survey._id}`}
                  class="button button-purple"
                >
                  <span class="button-text"></span>
                  Edit
                </a>
                <!--<a href={`./account/results_survey?survey=${survey._id}`} class="button button-purple"><span class="material-symbols-outlined"></span>Results</a>-->
                
                <button
                  on:click={() => deleteSurvey(survey._id)}
                  class="button button-delete"
                >
                  <svg
                    class="delete-top"
                    viewBox="0 0 39 7"
                    fill="none"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <line y1="5" x2="39" y2="5" stroke="white" stroke-width="4"
                    ></line>
                    <line
                      x1="12"
                      y1="1.5"
                      x2="26.0357"
                      y2="1.5"
                      stroke="white"
                      stroke-width="3"
                    ></line>
                  </svg>
                  <svg
                    class="delete-bottom"
                    viewBox="0 0 33 39"
                    fill="none"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <mask id="path-1-inside-1_8_19" fill="white">
                      <path
                        d="M0 0H33V35C33 37.2091 31.2091 39 29 39H4C1.79086 39 0 37.2091 0 35V0Z"
                      ></path>
                    </mask>
                    <path
                      d="M0 0H33H0ZM37 35C37 39.4183 33.4183 43 29 43H4C-0.418278 43 -4 39.4183 -4 35H4H29H37ZM4 43C-0.418278 43 -4 39.4183 -4 35V0H4V35V43ZM37 0V35C37 39.4183 33.4183 43 29 43V35V0H37Z"
                      fill="white"
                      mask="url(#path-1-inside-1_8_19)"
                    ></path>
                    <path d="M12 6L12 29" stroke="white" stroke-width="4"
                    ></path>
                    <path d="M21 6V29" stroke="white" stroke-width="4"></path>
                  </svg>
                </button>

                <button
                  on:click={download_survey(survey._id, survey.title)}
                  class="button button-purple"
                >
                  <span class="material-symbols-outlined">Download</span>
              </button>
              </div>
            </div>
          </div>
        </swiper-slide>
      {/each}
    </swiper-container>
  </div>
{/if}

<Modal
  bind:showModal
  clearFieldsOnClose
  cancelFunction={() => {
    title = "";
  }}
  doneFunction={async () => {
    if (!title) {
      errorTextModal =
        "Please enter a valid survey name in each of the fields.";
      showModal = true;
      return;
    }
    postSurvey();
  }}
>
  <span slot="header" class="modal__title">New survey</span>
  <div class="input" slot="content">
    <label class="input__label">Survey title</label>
    <input class="input__field" type="text" bind:value={title} />
    <p class="input__description">
      The title must contain a maximum of 32 characters
    </p>
    <label class="input__label">Survey description</label>
    <input class="input__field" type="text" />
    <p class="input__description">Enter a description for the survey</p>
  </div>
  <p class="error-text">{errorTextModal}</p>
</Modal>

<style>
  @import "/static/css/nullify.css";
  @import "/static/css/card.css";
  @import "/static/css/button.css";
  @import "/static/css/modal.css";
  @import "/static/css/fonts.css";
</style>
