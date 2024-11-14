<script lang="ts">
    import Modal from "../../Modal.svelte";
    import { getCookie, setCookie } from "$lib/cookie";
    import { refreshTokens } from "$lib/refresh";
    import { onMount } from "svelte";
    import { writable } from "svelte/store";
    import { api } from "$lib/API";
    import Fa from 'svelte-fa'
    import { faCirclePlus } from '@fortawesome/free-solid-svg-icons'

    let urlParams;
    let surveyId: string | null;
    let errorText = "";
    let showModal = false;
    let showEditModal = false;
    let variableName = "";
    let variableRange = "";
    let editVariableName = "";
    let editVariableRange = "";
    let myTable: HTMLTableElement;
    let survey: any;
    let clicked_row: number;
    let surveyPrompt = "";
    let surveyErrorPrompt = "";
    const update = {};

    let data = [
        { gender: ["Male", "Female", "Androgynous"] },
        { eyecolor: ["Blue", "Green", "Grey", "Brown", "Hazel"] },
        { eyesize: ["Small", "Medium", "Large"] },
        {
            haircolour: [
                "Blonde",
                "Black",
                "Red",
                "Brown",
                "Green",
                "White",
                "Grey",
                "Pink",
            ],
        },
        { hairlength: ["Bald", "Short", "Medium", "Long"] },
        { hairstructure: ["Straight", "Wavy", "Small Curl", "Big Curl"] }, // Only shown if not bald
        { skincolour: ["Very Light", "Light", "Medium", "Tan", "Dark"] },
        { nose: ["Small", "Medium", "Big"] },
        { mouth: ["Small", "Medium", "Big"] },
        { earsize: ["Small", "Medium", "Big"] },
        { facewidth: ["Thin", "Medium", "Wide"] },
        { facialhair: ["Clean Shaven", "Little Beard", "Beard"] },
        { glasses: ["With Glasses", "Without Glasses"] },
        { stature: ["Thin", "Regular", "Obese"] },
        { agerange: [] },
    ];

    let selectedOptions: Map<string, []> = new Map();

    let errorAge = "";
    let minAge: number;
    let maxAge: number;
    let newString: string;

    let selectedValues: Map<string, []> = new Map();
    let preVariablesData;

    async function editGenVar() {
        if (editVariableName == "" || editVariableRange == "") {
            errorText = "Please enter a valid option in each of the fields.";
            showEditModal = true;
        } else {
            let genVarArr = survey.generativeVariables;
            genVarArr[clicked_row] = {
                name: editVariableName,
                range: editVariableRange,
            };
            const update = { generativeVariables: genVarArr };

            await api
                .fetch(
                    "survey/edit",
                    "patch",
                    {
                        "Content-Type": "application/json",
                        Authorization: `Bearer ${getCookie("access_token")}`,
                    },
                    {
                        body: JSON.stringify({
                            _id: survey._id,
                            updates: update,
                        }),
                    },
                )
                .then(async (response) => {
                    // Token expired
                    if (response.status == 401) {
                        const tokens = await refreshTokens();

                        // Save tokens as cookies
                        setCookie("access_token", tokens["accessToken"]);
                        setCookie("refresh_token", tokens["refreshToken"]);

                        // Try again
                        return postGenVar();
                    }
                    if (response.status != 200) {
                        errorText =
                            "An unexpected server-error occured, please try again later.";
                        showEditModal = true;
                    } else {
                        editVariableName = "";
                        editVariableRange = "";
                        errorText = "";
                        showEditModal = false;
                    }
                })
                .catch((error) => {
                    console.error(error);
                    showEditModal = true;
                    errorText =
                        "An unexpected server-error occured, please try again later.";
                });

            await getGenVar();
        }
    }

    async function getGenVar() {
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
                    return getGenVar();
                }
                if (response.status != 200) {
                    errorText =
                        "An unexpected server-error occured, please try again later.";
                } else {
                    const result = await response.data;

                    //clear table
                    myTable.innerHTML = `<tr>
                        <th>Name</th>
                        <th>Range</th>
                    </tr>`;

                    //GENERATIVE variables
                    survey = result;
                    console.log(survey);
                    const genVars = survey.generativeVariables;
                    genVars.forEach(
                        (
                            genVar: { name: string; range: string },
                            i: number,
                        ) => {
                            var row = myTable.insertRow();
                            var cell1 = row.insertCell(0);
                            var cell2 = row.insertCell(1);
                            row.addEventListener("click", (event) => {
                                if (
                                    event.target == cell1 ||
                                    event.target == cell2
                                ) {
                                    showEditModal = true;

                                    clicked_row = i;

                                    editVariableName =
                                        survey.generativeVariables[i].name;
                                    editVariableRange =
                                        survey.generativeVariables[i].range;
                                }
                            });

                            var delCell = row.insertCell(2);

                            delCell.innerHTML =
                                '<span class="material-symbols-outlined">delete</span>';
                            delCell.className = "button button-red button-icon";
                            delCell.onclick = () => {
                                if (
                                    confirm(
                                        "Are you sure you want to delete this Variable?",
                                    )
                                ) {
                                    deleteGenVar(i);
                                }
                            };
                            cell1.innerHTML = genVar.name;
                            cell2.innerHTML = genVar.range;
                        },
                    );

                    const preVariables = survey.preVariables;
                    selectedOptions.clear();

                    if (preVariables) {
                        Object.entries(preVariables).forEach(
                            ([header, options]) => {
                                if (options instanceof Array) {
                                    options.forEach((option) => {
                                        console.log(option);
                                        recheckCheckboxChange(
                                            { target: { checked: true } },
                                            header,
                                            option,
                                        );
                                    });
                                }
                            },
                        );

                        if (
                            preVariables.agerange &&
                            preVariables.agerange.length == 2
                        ) {
                            console.log(preVariables.agerange);
                            minAge = preVariables.agerange[0];
                            maxAge = preVariables.agerange[1];
                        }
                    }
                    updateSurveyPrompt();
                }
            })
            .catch((error) => {
                errorText =
                    "An unexpected server-error occured, please try again later.";
                console.log(error);
            });

        if (survey.prompt) {
            surveyPrompt = survey.prompt;
        }
    }

    function recheckCheckboxChange(
        { target: { checked } }: ChangeEvent<HTMLInputElement>,
        header: string,
        option: string,
    ) {
        const checkboxes = document.querySelectorAll(
            `input[type="checkbox"][name="${header}"]`,
        );
        checkboxes.forEach((checkbox: HTMLInputElement) => {
            if (checkbox.nextSibling?.data === option) {
                checkbox.checked = checked;
                let options = selectedOptions.get(header) || [];
                if (!options.includes(option)) {
                    options.push(option);
                }
                selectedOptions.set(header, options);
            }
        });
    }

    async function postVar() {
        await api
            .fetch(
                "survey/edit",
                "patch",
                {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${getCookie("access_token")}`,
                },
                {
                    _id: surveyId,
                    updates: {
                        preVariables: preVariablesData,
                        prompt: surveyPrompt,
                    },
                },
            )
            .then(async (response) => {
                // Token expired
                if (response.status == 401) {
                    const tokens = await refreshTokens();

                    // Save tokens as cookies
                    setCookie("access_token", tokens["accessToken"]);
                    setCookie("refresh_token", tokens["refreshToken"]);

                    // Try again
                    return postGenVar();
                }
                if (response.status != 200) {
                    errorText =
                        "An unexpected server-error occured, please try again later.";
                    showModal = true;
                }
            })
            .catch((error) => {
                console.error(error);
                showModal = true;
                errorText =
                    "An unexpected server-error occured, please try again later.";
            });
        console.log("waiting for geVar .....");
        console.log(survey.preVariables);
        await getGenVar();
    }

    async function postGenVar() {
        if (variableName == "" || variableRange == "") {
            errorText = "Please enter a valid option in each of the fields.";
            showModal = true;
        } else {
            let genVarArr = survey.generativeVariables;
            genVarArr.push({ name: variableName, range: variableRange });
            const update = { generativeVariables: genVarArr };

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
                        return postGenVar();
                    }
                    if (response.status != 200) {
                        errorText =
                            "An unexpected server-error occured, please try again later.";
                        showModal = true;
                    } else {
                        variableName = "";
                        variableRange = "";
                        errorText = "";
                        showModal = false;
                    }
                })
                .catch((error) => {
                    console.error(error);
                    showModal = true;
                    errorText =
                        "An unexpected server-error occured, please try again later.";
                });

            await getGenVar();
        }
    }

    async function deleteGenVar(i: number) {
        let genVarArr = survey.generativeVariables;
        genVarArr.splice(i, 1);
        const update = { generativeVariables: genVarArr };

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
                if (response.status != 200) {
                    errorText =
                        "An unexpected server-error occured, please try again later.";
                } else {
                    errorText = "";
                }
            })
            .catch((error) => {
                console.error(error);
                errorText =
                    "An unexpected server-error occured, please try again later.";
            });

        await getGenVar();
    }

    function handleCheckboxChange(
        event: ChangeEvent<HTMLInputElement>,
        header: string,
        option: string,
    ) {
        const isChecked = event.target.checked;
        console.log(event.target);
        if (isChecked) {
            let options = selectedOptions.get(header) || [];
            if (!options.includes(option)) {
                options.push(option);
            }
            selectedOptions.set(header, options);
        } else {
            let options = selectedOptions.get(header) || [];
            options = options.filter((item) => item !== option);
            selectedOptions.set(header, options);
        }
        const selectedOptionsArray = Array.from(selectedOptions.entries());
        // localStorage.setItem(
        //     "selectedOptions",
        //     JSON.stringify(selectedOptionsArray),
        // );
        // console.log("Saved selected options to localStorage:", selectedOptions);
        updateSurveyPrompt();
    }

    function updateSurveyPrompt() {
        let isAgeActive = !(minAge == 0 && maxAge == 100);
        let isGenderActive = selectedOptions.has("gender");

        if (isAgeActive && isGenderActive) {
            newString = "@agerange y.o @gender with ";
        } else if (!isGenderActive && isAgeActive) {
            newString = "@agerange y.o person with ";
        } else if (!isAgeActive && isGenderActive) {
            newString = "@gender with ";
        } else {
            newString = "Person with ";
        }
        surveyErrorPrompt = "";
        let variablesString = "";
        let promptLength = newString.length;
        selectedOptions.forEach((options, header) => {
            if (header == "gender") {
                return;
            }
            if (!(options.length == 0)) {
                let largestOptionLength = 0;
                options.forEach((option: string) => {
                    largestOptionLength =
                        option.length > largestOptionLength
                            ? option.length
                            : largestOptionLength;
                });
                let part = "@" + header + " " + header + ", ";
                let partLength =
                    part.length - header.length - 1 + largestOptionLength;
                //let partLength = part.length
                variablesString += part;
                promptLength += partLength;
            }
        });

        if (!(variablesString == "")) {
            variablesString = variablesString.slice(0, -2);
            promptLength -= 2;
        }
        if (promptLength >= 77) // 77 is max characters for AI prompt image generation
        {
            surveyErrorPrompt = "With current variables the prompt may exceed the 77 character limit for image generation, please consider removing some variables."
        }
        surveyPrompt = newString + variablesString;
    }

    function handleMinAgeInput(event: Event) {
        if ((event.target as HTMLInputElement).value) {
            minAge = parseInt((event.target as HTMLInputElement).value);
        }
    }

    function handleMaxAgeInput(event: Event) {
        if ((event.target as HTMLInputElement).value) {
            maxAge = parseInt((event.target as HTMLInputElement).value);
        }
    }

    function saveSelectedOptions() {
        if (maxAge < minAge) {
            errorAge = "Maximum age cannot be smaller than minimum age.";
            return; // Prevent saving
        } else if (maxAge > 100) {
            errorAge = "Maximum age cannot be larger than 100 years old.";
            return; // Prevent saving
        }
        if (minAge == null) {
            minAge = 0;
        }

        if (maxAge == null) {
            maxAge = 100;
        }

        preVariablesData = {
            gender: [],
            eyecolor: [],
            eyesize: [],
            haircolour: [],
            hairlength: [],
            hairstructure: [],
            skincolour: [],
            nose: [],
            mouth: [],
            earsize: [],
            facewidth: [],
            facialhair: [],
            glasses: [],
            stature: [],
            agerange: [minAge, maxAge], // Assigning minAge and maxAge to agerange
        };
        data.forEach((item) => {
            for (const [header, options] of Object.entries(item)) {
                if (header !== "agerange") {
                    options.forEach((option) => {
                        if (
                            selectedOptions.has(header) &&
                            selectedOptions.get(header).includes(option)
                        ) {
                            preVariablesData[header].push(option);
                        }
                    });
                }
            }
        });

        console.log(selectedValues);

        postVar();
    }

    onMount(() => {
        urlParams = new URLSearchParams(window.location.search);
        surveyId = urlParams.get("survey");
        getGenVar();
    });
</script>

<div class="container-column">
    <h1 class="title">Variables</h1>
    <div class="variableColumn">
        {#each data as item}
            <div class="variable-card">
                {#each Object.entries(item) as [header, options]}
                    <div class="variable-row">
                        <h2 class="card-header">{header}</h2>
                        <div class="options-container">
                            {#if header !== "agerange"}
                                {#each options as option}
                                    <label class="cbx-label">
                                        <input
                                            type="checkbox"
                                            class="cbx"
                                            name={header}
                                            on:change={(event) =>
                                                handleCheckboxChange(
                                                    event,
                                                    header,
                                                    option,
                                                )}
                                        />{option}
                                    </label>
                                {/each}
                            {:else}
                                <div class="agerange-input">
                                    <div class="input-box" style="margin-bottom: 10px;">
                                        <input
                                            type="number"
                                            min="0"
                                            max="100"
                                            bind:value={minAge}
                                            placeholder="Enter a min value..."
                                            on:input={handleMinAgeInput}
                                        />
                                        <span>Min Age :</span>
                                    </div>
                                    <div class="input-box">
                                        <input
                                        type="number"
                                        min="0"
                                        max="100"
                                        bind:value={maxAge}
                                        placeholder="Enter a max value..."
                                        on:input={handleMaxAgeInput}
                                        />
                                        <span>Max Age :</span>
                                    </div>
                                </div>
                            {/if}
                        </div>
                    </div>
                {/each}
            </div>
        {/each}
    </div>
    <p class="error-text">{errorAge}</p>
    <button class="button button-blue button-save" style="margin-top: 40px;" on:click={saveSelectedOptions}>Save</button>

    <div class="prompt-container">
        <p class="prompt">
            <span class="prompt-header"
                >Generated prompt:
            </span>{surveyPrompt || "A prompt is loading..."}
        </p>
        {#if !(surveyErrorPrompt == "")}
            <p class="prompt" style="color:red;">
                {surveyErrorPrompt}
            </p>
        {/if}
        <p class="info">
            ** The values with @value wil be replaced with your options that you
            picked **
        </p>
    </div>

    <h1>Generative variables</h1>
    <table bind:this={myTable}></table>
    <!-- svelte-ignore a11y-click-events-have-key-events -->

    <div
        class="button button-blue"
        role="button"
        tabindex="-1"
        on:click={() => (showModal = true)}
    >
        <p style="margin-right:12px">Add a variable</p>
        <Fa icon={faCirclePlus}/>
    </div>
</div>

<Modal
    bind:showModal={showEditModal}
    doneText="save"
    cancelText="cancel"
    doneFunction={editGenVar}
>
    <span slot="header" class="modal__title">Add variable</span>

    <div class="input" slot="content">
        <h2>Name</h2>
        <input
            type="text"
            bind:value={editVariableName}
            placeholder="eg. hair color, age or gender"
        />

        <h2>Range</h2>
        <input
            type="text"
            bind:value={editVariableRange}
            placeholder="eg. 0-100 or red, green, blue"
        />

        <p>
            Use two numbers separated by a hyphen (eg. 0-100) for a numeric
            range or a comma-separated list (eg. red, green, blue) for a
            discrete range.
        </p>

        <p class="error-text">{errorText}</p>
    </div>
</Modal>

<Modal bind:showModal clearFieldsOnClose doneFunction={postGenVar}>
    <span slot="header" class="modal__title">Add variable</span>

    <div class="input" slot="content">
        <h2>Name</h2>
        <input
            type="text"
            bind:value={variableName}
            placeholder="eg. hair color, age or gender"
        />

        <h2>Range</h2>
        <input
            type="text"
            bind:value={variableRange}
            placeholder="eg. 0-100 or red, green, blue"
        />

        <p>
            Use two numbers separated by a hyphen (eg. 0-100) for a numeric
            range or a comma-separated list (eg. red, green, blue) for a
            discrete range.
        </p>

        <p class="error-text">{errorText}</p>
    </div>
</Modal>

<style>
    @import "/static/css/table.css";
    @import "/static/css/modal.css";
    @import "/static/css/generative.css";
    @import "/static/css/button.css";
    @import "/static/css/fonts.css";
    @import "/static/css/header.css";
    @import "@fortawesome/fontawesome-free/css/all.min.css";
</style>
