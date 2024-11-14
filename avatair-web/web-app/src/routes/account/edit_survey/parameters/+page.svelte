<script lang="ts">
    import Switch from "../Switch.svelte";
    import { getCookie, setCookie } from "$lib/cookie";
    import { refreshTokens } from "$lib/refresh";
    import { onMount } from "svelte";
    import { api } from "$lib/API";

    let parameters = {
        maxIterations: 0,
        avatarsPerPage: 0,
        abort: false,
        explainDecision: false,
        explainRequired: false,
        generateAvatar: false,
        webcam: false,
        imageUpload: false,
        welcomePage: false,
        endPage: false,
        finalSelection: false,
    };

    let surveyId: string | null;
    let urlParams;
    let survey: any;

    let errorText = "";
    let saveButton: HTMLElement;

    async function getParameters() {
        await api
            .fetch("survey/" + surveyId, "get", {
                "Content-Type": "application/json",
                Authorization: `Bearer ${getCookie("access_token")}`,
            })
            .then(async (response) => {
                // Token expired
                if (response.status == 401) {
                    const tokens = await refreshTokens();

                    // Save tokens as cookies
                    setCookie("access_token", tokens["accessToken"]);
                    setCookie("refresh_token", tokens["refreshToken"]);

                    // Try again
                    return getParameters();
                }
                if (response.status != 200) {
                    errorText =
                        "An unexpected server-error occured, please try again later.";
                } else {
                    survey = await response.data;
                    parameters.maxIterations = survey.parameters.maxIterations;
                    parameters.avatarsPerPage =
                        survey.parameters.avatarsPerPage;
                    parameters.abort = survey.parameters.abort;
                    parameters.explainDecision =
                        survey.parameters.explainDecision;
                    parameters.explainRequired =
                        survey.parameters.explainRequired;
                    parameters.generateAvatar =
                        survey.parameters.generateAvatar;
                    parameters.webcam = survey.parameters.webcam;
                    parameters.imageUpload = survey.parameters.imageUpload;
                    parameters.welcomePage = survey.parameters.welcomePage;
                    parameters.endPage = survey.parameters.endPage;
                    parameters.finalSelection =
                        survey.parameters.finalSelection;

                    errorText = "";
                }
            })
            .catch((error) => {
                errorText =
                    "An unexpected server-error occured, please try again later.";
            });
    }

    async function postParameters() {
        const update = { parameters: parameters };
        await api
            .fetch(
                "/survey/edit",
                "patch",
                {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${getCookie("access_token")}`,
                },
                { _id: surveyId, updates: update },
            )
            .then(async (response) => {
                // Token expired
                if (response.status == 401) {
                    const tokens = await refreshTokens();

                    // Save tokens as cookies
                    setCookie("access_token", tokens["accessToken"]);
                    setCookie("refresh_token", tokens["refreshToken"]);

                    // Try again
                    return postParameters();
                }
                if (response.status != 200) {
                    errorText =
                        "An unexpected server-error occured, please try again later.";
                } else {
                    errorText = "";
                    saveButton.style.opacity = "0";
                }
            })
            .catch((error) => {
                errorText =
                    "An unexpected server-error occured, please try again later.";
            });
    }

    function showButton() {
        saveButton.style.opacity = "1";
    }

    onMount(() => {
        urlParams = new URLSearchParams(window.location.search);
        surveyId = urlParams.get("survey");
        getParameters();
    });
</script>

<p class="error-text">{errorText}</p>

<button
    class="button button-green button-fade"
    id="button-fixed"
    bind:this={saveButton}
    on:click={postParameters}>Save changes</button
>

<div id="settings" class="container-column">
    <div class="setting">
        <div>
            <h3>Max Iterations</h3>
            <p>How many iterations to generate</p>
        </div>
        <input
            on:input={showButton}
            min="1"
            max="10"
            type="number"
            id="MaxIte"
            bind:value={parameters.maxIterations}
        />
    </div>
    <hr />
    <div class="setting">
        <div>
            <h3>Avatars Per Page</h3>
            <p>How many avatars to generate per iteration</p>
        </div>
        <input
            on:input={showButton}
            min="2"
            max="8"
            type="number"
            id="AvaIte"
            bind:value={parameters.avatarsPerPage}
        />
    </div>
    <hr />
    <div class="setting">
        <div>
            <h3>User aborts iterations</h3>
            <p>Allow user to abort the survey</p>
        </div>
        <Switch on:click={showButton} bind:checked={parameters.abort} />
    </div>
    <hr />
    <div class="setting">
        <div>
            <h3>Explain decisions</h3>
            <p>Let the user explain why they made their decision</p>
        </div>
        <Switch
            on:click={showButton}
            bind:checked={parameters.explainDecision}
        />
    </div>
    <hr />
    <div class="setting">
        <div>
            <h3>Explaination is mandatory</h3>
            <p>Make explanation mandatory</p>
        </div>
        <Switch
            on:click={showButton}
            bind:checked={parameters.explainRequired}
        />
    </div>
    <hr />
    <div class="setting">
        <div>
            <h3>Generate user avatars</h3>
            <p>Generate avatars based on the users photo</p>
        </div>
        <Switch
            on:click={showButton}
            bind:checked={parameters.generateAvatar}
        />
    </div>
    <hr />
    <div class="setting">
        <div>
            <h3>Enable webcam</h3>
            <p>Allow the user to take their own photo</p>
        </div>
        <Switch on:click={showButton} bind:checked={parameters.webcam} />
    </div>
    <hr />
    <div class="setting">
        <div>
            <h3>Enable image upload</h3>
            <p>Allow the user to upload their own photo</p>
        </div>
        <Switch on:click={showButton} bind:checked={parameters.imageUpload} />
    </div>
    <hr />
    <div class="setting">
        <div>
            <h3>Display welcome page</h3>
            <p>Display welcome page at the start of the survey</p>
        </div>
        <Switch on:click={showButton} bind:checked={parameters.welcomePage} />
    </div>
    <hr />
    <div class="setting">
        <div>
            <h3>Display end page</h3>
            <p>Display end page at the end of the survey</p>
        </div>
        <Switch on:click={showButton} bind:checked={parameters.endPage} />
    </div>
    <hr />
    <div class="setting">
        <div>
            <h3>Allow final selection</h3>
            <p>
                Allow the user to pick a final avatar at the end of the survey
            </p>
        </div>
        <Switch
            on:click={showButton}
            bind:checked={parameters.finalSelection}
        />
    </div>
</div>

<style>
    @import "/static/css/fonts.css";

    input {
        height: 24px;
        margin: 0 40px;
    }

    #settings {
        margin-bottom: 50px;
    }

    .setting {
        width: 80%;
        max-width: 900px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .setting h3 {
        font-family: inherit;
    }

    hr {
        width: 80%;
        max-width: 900px;
        border: hsl(0, 0%, 90%) solid 1px;
    }
    .container-column {
        padding: 1rem;
    }
</style>
