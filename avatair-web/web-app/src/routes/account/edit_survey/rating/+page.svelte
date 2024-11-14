<script lang="ts">
    import Modal from "../../Modal.svelte";
    import { getCookie, setCookie } from "$lib/cookie";
    import { refreshTokens } from "$lib/refresh";
    import { onMount } from "svelte";
    import Fa from 'svelte-fa'
    import { faCirclePlus } from '@fortawesome/free-solid-svg-icons'
    import Slider from "@bulatdashiev/svelte-slider";
    import StarRating from "@ernane/svelte-star-rating";
    import { api } from "$lib/API";

    const config = {
        readOnly: false,
        countStars: 5,
        range: {
            min: 0,
            max: 5,
            step: 0.5,
        },
        score: 0.0,
        showScore: false,
        scoreFormat: function () {
            return `(${this.score.toFixed(0)}/${this.countStars})`;
        },
        name: "",
        starConfig: {
            size: 30,
            fillColor: "#83BBFD",
            strokeColor: "#222FA8",
            unfilledColor: "#D9D9D9",
            strokeUnfilledColor: "#000",
        },
    };

    let errorText = "";
    let infoText = "";

    let ratingName = "";
    let ratingType = "";
    let ratingLabelBad = "";
    let ratingLabelGood = "";
    let ratingText = "";

    let ratingEditName = "";
    let ratingEditType = "";
    let ratingEditLabelBad = "";
    let ratingEditLabelGood = "";
    let ratingEditText = "";

    let myTable: HTMLTableElement;
    let urlParams;
    let surveyId: string | null;
    let survey: any;

    let showModal = false;
    let showEditModal = false;

    let clicked_row: number;

    async function editRating() {
        if (
            ratingEditName == "" ||
            ratingEditType == "" ||
            ratingEditLabelBad == "" ||
            ratingEditLabelGood == ""
        ) {
            errorText = "Please enter a valid option in each of the fields.";
            showEditModal = true;
        } else {
            let ratingScalesArr = survey.ratingScales;
            ratingScalesArr[clicked_row] = {
                name: ratingEditName,
                text: ratingEditText,
                type: ratingEditType,
                labelGood: ratingEditLabelGood,
                labelBad: ratingEditLabelBad,
            };

            const update = { ratingScales: ratingScalesArr };
            await api
                .fetch(
                    "survey/edit",
                    "patch",
                    {
                        "Content-Type": "application/json",
                        Authorization: `Bearer ${getCookie("access_token")}`,
                    },
                    { _id: survey._id, updates: update },
                )
                .then(async (response) => {
                    // Token expired
                    if (response.status == 401) {
                        const tokens = await refreshTokens();

                        // Save tokens as cookies
                        setCookie("access_token", tokens["accessToken"]);
                        setCookie("refresh_token", tokens["refreshToken"]);

                        // Try again
                        return postRatingScale();
                    }
                    if (response.status != 200) {
                        errorText =
                            "An unexpected server-error occured, please try again later.";
                        showEditModal = true;
                    } else {
                        ratingEditName = "";
                        ratingEditType = "";
                        ratingEditLabelBad = "";
                        ratingEditLabelGood = "";
                        ratingEditText = "";

                        errorText = "";
                        infoText = "";
                        showEditModal = false;
                    }
                })
                .catch((error) => {
                    console.error(error);
                    showEditModal = true;
                    errorText =
                        "An unexpected server-error occured, please try again later.";
                });
            await getRatingScales();
        }
    }

    async function getRatingScales() {
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
                    return getRatingScales();
                }

                if (response.status != 200) {
                    errorText =
                        "An unexpected server-error occured, please try again later.";
                    return;
                }

                errorText = "";
                const result = await response.data;
                survey = result;

                //clear table
                myTable.innerHTML = `<tr>
                <th>Name</th>
                <th>Type</th>
                <th>Text</th>
                <th colspan="2">Labels</th>
            </tr>`;

                const ratingScales = survey.ratingScales;

                if (survey.ratingScales.length == 0) {
                    infoText =
                        "There needs to be atleast one Rating Scale for the survey to be functional. Please add atleast one Rating Scale.";
                }

                ratingScales.forEach(
                    (
                        ratingScale: {
                            name: string;
                            type: string;
                            text: string;
                            labelGood: string;
                            labelBad: string;
                        },
                        i: number,
                    ) => {
                        var row = myTable.insertRow();
                        var cell1 = row.insertCell(0);
                        var cell2 = row.insertCell(1);
                        var cell3 = row.insertCell(2);
                        var cell4 = row.insertCell(3);
                        var cell5 = row.insertCell(4);
                        var delCell = row.insertCell(5);

                        row.addEventListener("click", (event) => {
                            if (
                                [cell1, cell2, cell3, cell4, cell5].includes(
                                    event.target,
                                )
                            ) {
                                showEditModal = true;
                                clicked_row = i;

                                ratingEditName = survey.ratingScales[i].name;
                                ratingEditType = survey.ratingScales[i].type;
                                ratingEditLabelBad =
                                    survey.ratingScales[i].labelBad;
                                ratingEditLabelGood =
                                    survey.ratingScales[i].labelGood;
                                ratingEditText = survey.ratingScales[i].text;
                            }
                        });

                        delCell.innerHTML =
                            '<span class="material-symbols-outlined">delete</span>';
                        delCell.className = "button button-red button-icon";
                        delCell.onclick = () => {
                            if (
                                confirm(
                                    "Are you sure you want to delete this Rating Scale?",
                                )
                            ) {
                                deleteRatingScale(i);
                            }
                        };
                        cell1.innerHTML = ratingScale.name;
                        cell2.innerHTML = ratingScale.type;
                        cell3.innerHTML = ratingScale.text;
                        cell4.innerHTML = ratingScale.labelGood;
                        cell5.innerHTML = ratingScale.labelBad;
                    },
                );
            })
            .catch((error) => {
                console.error(error);
                errorText =
                    "An unexpected server-error occured, please try again later.";
            });
    }

    async function postRatingScale() {
        if (
            ratingName == "" ||
            ratingType == "" ||
            ratingLabelBad == "" ||
            ratingLabelGood == ""
        ) {
            errorText = "Please enter a valid option in each of the fields.";
            showModal = true;
        } else {
            let ratingScalesArr = survey.ratingScales;
            ratingScalesArr.push({
                name: ratingName,
                text: ratingText,
                type: ratingType,
                labelGood: ratingLabelGood,
                labelBad: ratingLabelBad,
            });
            const update = { ratingScales: ratingScalesArr };
            await api
                .fetch(
                    "survey/edit",
                    "patch",
                    {
                        "Content-Type": "application/json",
                        Authorization: `Bearer ${getCookie("access_token")}`,
                    },
                    { _id: survey._id, updates: update },
                )
                .then(async (response) => {
                    // Token expired
                    if (response.status == 401) {
                        const tokens = await refreshTokens();

                        // Save tokens as cookies
                        setCookie("access_token", tokens["accessToken"]);
                        setCookie("refresh_token", tokens["refreshToken"]);

                        // Try again
                        return postRatingScale();
                    }
                    if (response.status != 200) {
                        errorText =
                            "An unexpected server-error occured, please try again later.";
                        showModal = true;
                    } else {
                        ratingName = "";
                        ratingType = "";
                        ratingLabelBad = "";
                        ratingLabelGood = "";
                        ratingText = "";

                        errorText = "";
                        infoText = "";
                        showModal = false;
                    }
                })
                .catch((error) => {
                    console.error(error);
                    showModal = true;
                    errorText =
                        "An unexpected server-error occured, please try again later.";
                });
            await getRatingScales();
        }
    }

    async function deleteRatingScale(i: number) {
        let ratingScalesArr = survey.ratingScales;
        ratingScalesArr.splice(i, 1);
        const update = { ratingScales: ratingScalesArr };

        await api
            .fetch(
                "survey/edit",
                "patch",
                {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${getCookie("access_token")}`,
                },
                { _id: survey._id, updates: update },
            )
            .then(async (response) => {
                if (response.status != 200)
                    errorText =
                        "An unexpected server-error occured, please try again later";
                const result = await response.data;
            })
            .catch((error) => {
                console.error(error);
                errorText =
                    "An unexpected server-error occured, please try again later";
            });
        await getRatingScales();
    }

    onMount(() => {
        urlParams = new URLSearchParams(window.location.search);
        surveyId = urlParams.get("survey");
        getRatingScales();
    });
</script>

<div class="container-column">
    <h1 class="title">Rating scales</h1>
    <p class="info-text">{infoText}</p>

    <table bind:this={myTable}></table>
    <!-- svelte-ignore a11y-click-events-have-key-events -->
    <div
        class="button button-blue"
        role="button"
        tabindex="-1"
        on:click={() => (showModal = true)}
    >
        <p style="margin-right: 4px;">Add a rating scale</p>
        <Fa style="margin-right: 4px;" icon={faCirclePlus}/>
    </div>
</div>

<Modal
    bind:showModal={showEditModal}
    doneText="save"
    cancelText="cancel"
    doneFunction={editRating}
>
    <span class="modal__title" slot="header">Edit ratingscale</span>

    <!-- Modal Body -->
    <div class="input" slot="content">
        <!-- Content for modal body goes here -->

        <label class="input__label">Name</label>
        <input
            class="input_field"
            type="text"
            bind:value={ratingName}
            placeholder="eg. Likeability, Trustiness, Beauty"
        />

        <h2>Type</h2>
        <label for="typedrop">Pick one of the following:</label>
        <select name="typedrop" id="typedrop" bind:value={ratingType}>
            <option value="Slider">Slider</option>
            <option value="Star Rating">Star Rating</option>
            <option value="Select">Select</option>
            <option value="Swipe">Swipe</option>
        </select>

        <h2>Text</h2>
        <p>
            Write a short explaination how the user should comprehend the rating
            scale.
        </p>
        <input
            type="text"
            bind:value={ratingText}
            placeholder="eg. Rate how much you like this avatar."
        />

        <h2>Label</h2>
        <p>
            Pick an alternative for each of the drop-down menus. The first
            drop-down will be the label for the bad rating, and the second
            drop-down will the label for the good rating.
        </p>
        <label for="typedrop">Pick one each of the following:</label>
        <select
            name="LabelDropBad"
            id="LabelDropBad"
            bind:value={ratingLabelBad}
        >
            <option value="0">0</option>
            <option value="Bad">Bad</option>
            <option value="👎">👎</option>
            <option value="☹️">☹️</option>
        </select>
        <select
            name="LabelDropBad"
            id="LabelDropBad"
            bind:value={ratingLabelGood}
        >
            <option value="100">100</option>
            <option value="Good">Good</option>
            <option value="👍">👍</option>
            <option value="🙂">🙂</option>
        </select>

        <h2>Preview</h2>
        <p>Here is a preview of the label you have created.</p>
        <div class="avatar-card" style="width: 50%;">
            {#if ratingType == "Slider"}
                <div class="rating slider">
                    <h3>{ratingName}</h3>
                    <div class="labels">
                        <p>{ratingLabelBad}</p>
                        <p>{ratingLabelGood}</p>
                    </div>
                    <Slider />
                    {#if ratingText != ""}
                        <p>{ratingText}</p>
                    {/if}
                </div>
            {:else if ratingType == "Star Rating"}
                <div class="rating stars">
                    <h3>{ratingName}</h3>
                    <div class="labels">
                        <p>{ratingLabelBad}</p>
                        <p>{ratingLabelGood}</p>
                    </div>
                    <StarRating {config} />
                    {#if ratingText != ""}
                        <p>{ratingText}</p>
                    {/if}
                </div>
            {/if}
        </div>

        <p class="error-text">{errorText}</p>
    </div>
</Modal>

<Modal bind:showModal clearFieldsOnClose doneFunction={postRatingScale}>
    <span class="modal__title" slot="header">Add ratingscale</span>

    <!-- Modal Body -->
    <div class="input" slot="content">
        <!-- Content for modal body goes here -->

        <label class="input__label">Name</label>
        <input
            class="input_field"
            type="text"
            bind:value={ratingName}
            placeholder="eg. Likeability, Trustiness, Beauty"
        />

        <h2>Type</h2>
        <label for="typedrop">Pick one of the following:</label>
        <select name="typedrop" id="typedrop" bind:value={ratingType}>
            <option value="Slider">Slider</option>
            <option value="Star Rating">Star Rating</option>
            <option value="Select">Select</option>
            <option value="Swipe">Swipe</option>
        </select>

        <h2>Text</h2>
        <p>
            Write a short explaination how the user should comprehend the rating
            scale.
        </p>
        <input
            type="text"
            bind:value={ratingText}
            placeholder="eg. Rate how much you like this avatar."
        />

        <h2>Label</h2>
        <p>
            Pick an alternative for each of the drop-down menus. The first
            drop-down will be the label for the bad rating, and the second
            drop-down will the label for the good rating.
        </p>
        <label for="typedrop">Pick one each of the following:</label>
        <select
            name="LabelDropBad"
            id="LabelDropBad"
            bind:value={ratingLabelBad}
        >
            <option value="0">0</option>
            <option value="Bad">Bad</option>
            <option value="👎">👎</option>
            <option value="☹️">☹️</option>
        </select>
        <select
            name="LabelDropBad"
            id="LabelDropBad"
            bind:value={ratingLabelGood}
        >
            <option value="100">100</option>
            <option value="Good">Good</option>
            <option value="👍">👍</option>
            <option value="🙂">🙂</option>
        </select>

        <h2>Preview</h2>
        <p>Here is a preview of the label you have created.</p>
        <div class="avatar-card" style="width: 50%;">
            {#if ratingType == "Slider"}
                <div class="rating slider">
                    <h3>{ratingName}</h3>
                    <div class="labels">
                        <p>{ratingLabelBad}</p>
                        <p>{ratingLabelGood}</p>
                    </div>
                    <Slider />
                    {#if ratingText != ""}
                        <p>{ratingText}</p>
                    {/if}
                </div>
            {:else if ratingType == "Star Rating"}
                <div class="rating stars">
                    <h3>{ratingName}</h3>
                    <div class="labels">
                        <p>{ratingLabelBad}</p>
                        <p>{ratingLabelGood}</p>
                    </div>
                    <StarRating {config} />
                    {#if ratingText != ""}
                        <p>{ratingText}</p>
                    {/if}
                </div>
            {/if}
        </div>

        <p class="error-text">{errorText}</p>
    </div>
</Modal>

<style>
    @import "static/css/nullify.css";
    @import "/static/css/table.css";
    @import "/static/css/modal.css";
    @import "/static/css/button.css";
    @import "/static/css/survey.css";
    @import "/static/css/header.css";
    @import "/static/css/fonts.css";

    .title{
        font-size: 30px;
        font-weight: 400;
    }
</style>
