

<script>
  import { createEventDispatcher } from "svelte";
  import Thumb from "./Thumb.svelte";

  const dispatch = createEventDispatcher();

  let name = [];
  let range = false;
  let min = 0;
  let max = 100;
  let step = 1;
  let value = [min, max];
  let pos = 0
  let active = false;
  let order = false;
  let current_value;

  export { name, range, min, max, step, value, order };
  
  export let componentRating = {
      type: "slider", 
      min: min, 
      max: max,
      score: pos,
  };

  $: {componentRating.score = pos}

  $: if (active) setValue(pos);
  $: if (!active) setPos(value);

  $: if (range && order && active) pos = checkPos(pos);

  $: min, max, clamp();

  $: progress = `
    left: ${range ? Math.min(pos[0], pos[1]) * 100 : 0}%;
    right: ${100 - Math.max(pos[0], (range ? pos[1] : pos[0])) * 100}%;
  `;

  

  function handleChange(event) {
  sliderValue = event.target.value;
  console.log("Slider value changed:", event.target.value);
  dispatch("change", newValue);
  }

  function setValue(pos) {
    const offset = min % step;
    const width = max - min
    value = pos
      .map(v => min + v * width)
      .map(v => Math.round((v - offset) / step) * step + offset);
    dispatch("input", value);
  }

  function setPos(value) {
    pos = value
      .map(v => Math.min(Math.max(v, min), max))
      .map(v => (v - min) / (max - min));
  }

  function checkPos(pos) {
    return [Math.min(...pos), Math.max(...pos)];
  }

  function clamp() {
    setPos(value);
    setValue(pos);
  }
</script>

<div class="slider-container">
  <input type="range" min="0" max="100" bind:value={value[0]} class="slider" on:change={handleChange}>
  <p>Score: {value[0]}</p>
</div>

<input type="number" value={value[0]} name={name[0]} />
{#if range}
  <input type="number" value={value[1]} name={name[1]} />
{/if}
<div class="track">
  <div
    class="progress"
    style={progress} />
  <Thumb bind:pos={pos[0]} on:active={({ detail: v }) => active = v}>
    <slot name="left">
      <slot>
        <div class="thumb" />
      </slot>
    </slot>
  </Thumb>
  {#if range}
    <Thumb bind:pos={pos[1]} on:active={({ detail: v }) => active = v}>
      <slot name="right">
        <slot>
          <div class="thumb" />
        </slot>
      </slot>
    </Thumb>
  {/if}
</div>

<style>
  input {
    display: none;
  }

  .track {
    margin: 16px 8px;
    position: relative;
    height: 4px;
    width: calc(100% - 16px);
    border-radius: 100vh;
    background: var(--track-bg, #ebebeb);
  }

  .progress {
    position: absolute;
    left: 0;
    right: 0;
    top: 0;
    bottom: 0;
    border-radius: 100vh;
    background: var(--progress-bg, #8abdff);
  }

  .thumb {
    width: 16px;
    height: 16px;
    border-radius: 100vh;
    background: var(--thumb-bg, #5784fd);
  }
</style>
