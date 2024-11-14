<script lang="ts">
    import { onMount } from "svelte";
    import Fa from 'svelte-fa'
    import { faArrowLeftLong } from '@fortawesome/free-solid-svg-icons'
    let urlParams;
    let surveyId: string | null;

    onMount (() => {
        urlParams = new URLSearchParams(window.location.search);
        surveyId = urlParams.get('survey');
    });
</script>

<a href="./?survey={surveyId}" class = "go-back">
    <Fa icon={faArrowLeftLong}/>
    <p style="margin-left:6px;">Go back</p>
</a>

<style>
    @import "/static/css/button.css";
</style>
<slot />
