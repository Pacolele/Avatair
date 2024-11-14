<script lang="ts">
    import { onMount } from "svelte";

    let urlParams;
    let surveyId: string | null;

    onMount (() => {
        urlParams = new URLSearchParams(window.location.search);
        surveyId = urlParams.get('survey');
    });
</script>

<a href="./?survey={surveyId}" class = "go-back">
    <span class="material-symbols-outlined">
        arrow_back
        </span>
    Go back
</a>

<style>
    @import "/static/css/button.css";
</style>
<slot />
