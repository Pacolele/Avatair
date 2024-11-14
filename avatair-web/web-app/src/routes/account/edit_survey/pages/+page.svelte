<script lang="ts">
    import Switch from "../Switch.svelte";
    import { getCookie, setCookie } from "$lib/cookie";
    import { refreshTokens } from "$lib/refresh";
    import { onMount } from "svelte";
    import { api } from "$lib/API";

    let displayWelcomePage: boolean;
    let displayEndPage: boolean;
    let welcomeInputTitle = "";
    let welcomeInputContent = "";
    let endInputContent = "";
    let endInputTitle = "";
    let survey: any;
    let surveyId: string | null;
    let urlParams;

    let saveButton: HTMLButtonElement;
    let errorText = "";

    async function getPages() {
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
                    return getPages();
                }
                if (response.status != 200) {
                    errorText =
                        "An unexpected server-error occured, please try again later.";
                } else {
                    survey = await response.data;
                    welcomeInputTitle = survey.welcomePage.title;
                    welcomeInputContent = survey.welcomePage.content;
                    endInputTitle = survey.endPage.title;
                    endInputContent = survey.endPage.content;
                    displayWelcomePage = survey.parameters.welcomePage;
                    displayEndPage = survey.parameters.endPage;
                    errorText = "";
                }
            })
            .catch((error) => {
                console.error(error);
                errorText =
                    "An unexpected server-error occured, please try again later.";
            });
    }

    async function postPages() {
        let newSurvey = survey;
        newSurvey.welcomePage.title = welcomeInputTitle;
        newSurvey.welcomePage.content = welcomeInputContent;
        newSurvey.endPage.title = endInputTitle;
        newSurvey.endPage.content = endInputContent;
        newSurvey.parameters.welcomePage = displayWelcomePage;
        newSurvey.parameters.endPage = displayEndPage;

        const update = newSurvey;
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
                // Token expired
                if (response.status == 401) {
                    const tokens = await refreshTokens();

                    // Save tokens as cookies
                    setCookie("access_token", tokens["accessToken"]);
                    setCookie("refresh_token", tokens["refreshToken"]);

                    // Try again
                    return postPages();
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
        getPages();
    });

    function onClickEquivalent() {
        if (saveButton.style.opacity == "1") {
            !confirm("Would you like to save your changes?");
        }
        return "";
    }
</script>

<a on:click={onClickEquivalent} href="" class="go-back">
    <span class="material-symbols-outlined"> </span>
</a>

<button
    class="button button-green button-fade"
    id="button-fixed"
    bind:this={saveButton}
    on:click={postPages}>Save changes</button
>

<div class="container-column">
    <h1>Pages</h1>
    <p class="info-text">
        To create 'Line Breaks', please use the &ltbr&gt-tag
    </p>

    <p class="error-text">{errorText}</p>
    <div class="pages">
        <center><h2>Welcome Page</h2></center>
        <hr />
        <Switch
            bind:checked={displayWelcomePage}
            on:click={showButton}
            label="Display Welcome Page"
        />
        Title<br /><input
            type="text"
            class="txtbox-title"
            on:focus={showButton}
            bind:value={welcomeInputTitle}
        />
        Content
        <textarea
            class="txtbox-content"
            cols="40"
            rows="15"
            bind:value={welcomeInputContent}
            on:input={showButton}
        ></textarea>
    </div>
    <div class="pages">
        <center><h2>Welcome Page Preview</h2></center>
        <hr />
        <di class="container-row">
            <h2>{welcomeInputTitle}</h2>
        </di>
        <p bind:innerHTML={welcomeInputContent} contenteditable="false"></p>
    </div>
    <hr />
    <div class="pages">
        <center><h2>End Page</h2></center>
        <hr />
        <Switch
            bind:checked={displayEndPage}
            on:click={showButton}
            label="Display End Page"
        />
        Title<br /><input
            type="text"
            class="txtbox-title"
            bind:value={endInputTitle}
            on:input={showButton}
        />
        Content
        <textarea
            class="txtbox-content"
            cols="40"
            rows="15"
            bind:value={endInputContent}
            on:input={showButton}
        ></textarea>
    </div>
    <div class="pages">
        <center><h2>End Page Preview</h2></center>
        <hr />
        <div class="container-row">
            <h2>{endInputTitle}</h2>
        </div>
        <p bind:innerHTML={endInputContent} contenteditable="false"></p>
    </div>
</div>

<style>
    @import "/static/css/fonts.css";
    @import "/static/css/pages.css";
    @import "/static/css/header.css";
    @import "/static/css/button.css";
</style>
