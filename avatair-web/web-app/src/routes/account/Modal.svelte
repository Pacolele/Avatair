<script lang="ts">
	export let showModal: boolean;
	export let doneText: string = "Add";
	export let cancelText: string = "Discard";
	export let doneFunction = async () => {};
	export let cancelFunction = () => {};
	export let clearFieldsOnClose = false;

	async function addButton() {
		await doneFunction();
	}
	function closeButton() {
		cancelFunction();
		dialog.close();
	}

	let dialog: HTMLDialogElement;

	$: if (dialog) {
		if (showModal) {
			dialog.showModal();
			dialog.scrollTo(0, 0); // Scroll to top
		} else {
			dialog.close();
		}
	}
</script>

<!-- svelte-ignore a11y-click-events-have-key-events a11y-no-noninteractive-element-interactions -->

{#if showModal}
	<dialog
		class="modal"
		bind:this={dialog}
		on:close={() => {
			// Clear input fields
			cancelFunction();
			if (clearFieldsOnClose) {
				dialog
					.querySelectorAll("input")
					.forEach((input) => (input.value = ""));
				dialog
					.querySelectorAll("select")
					.forEach((select) => (select.value = ""));
			}

			showModal = false;
		}}
	>
		<!-- Modal Header -->
		<div class="modal__header">
			<slot name="header" />
		</div>
		<!-- Modal Body -->
		<div class="modal__body">
			<!-- Content for modal body goes here -->
			<slot name="content" />
		</div>
		<!-- Modal Footer -->
		<div class="modal__footer">
			<button
				class="modal-button button-cancel"
				tabindex="-1"
				on:click={closeButton}
				><span class="text">{cancelText}</span><span class="icon">
					<svg
						xmlns="http://www.w3.org/2000/svg"
						width="24"
						height="24"
						viewBox="0 0 24 24"
					>
						<path
							d="M24 20.188l-8.315-8.209 8.2-8.282-3.697-3.697-8.212 8.318-8.31-8.203-3.666 3.666 8.321 8.24-8.206 8.313 3.666 3.666 8.237-8.318 8.285 8.203z"
						>
						</path>
					</svg>
				</span>
			</button>
			<button
				class="modal-button button-done"
				tabindex="-1"
				on:click={addButton}
				><span class="text">{doneText}</span><span class="icon">
					<svg
						xmlns="http://www.w3.org/2000/svg"
						width="24"
						height="24"
						viewBox="0 0 24 24"
					>
						<path
							d="M19 11H13V5a1 1 0 0 0 -2 0v6H5a1 1 0 0 0 0 2h6v6a1 1 0 0 0 2 0V13h6a1 1 0 0 0 0 -2z"
						/>
					</svg>
				</span>
			</button>
		</div>
	</dialog>
{/if}

<style>
	@import "/static/css/button.css";

	dialog {
		position: absolute;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		width: 50%;
		height: 50%;
		display: flex;
		align-items: center;
		justify-content: center;
		flex-direction: column;
		padding: 1.5rem;
	}

	dialog::backdrop {
		background: rgba(0, 0, 0, 0.3);
	}

	dialog[open] {
		animation: zoom 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
	}

	@keyframes zoom {
		from {
			transform: scale(0.95);
		}
		to {
			transform: scale(1);
		}
	}

	dialog[open]::backdrop {
		animation: fade 0.2s ease-out;
	}

	@keyframes fade {
		from {
			opacity: 0;
		}
		to {
			opacity: 1;
		}
	}

	.button-cancel {
		width: 150px;
		height: 50px;
		cursor: pointer;
		display: flex;
		align-items: center;
		background: red;
		border: none;
		border-radius: 5px;
		box-shadow: 1px 1px 3px rgba(0, 0, 0, 0.15);
		background: #e62222;
	}

	.modal-button,
	.modal-button span {
		transition: 200ms;
	}

	.modal-button .text {
		transform: translateX(35px);
		color: white;
		font-weight: bold;
	}

	.button-cancel .icon {
		position: absolute;
		border-left: 1px solid #c41b1b;
		transform: translateX(110px);
		height: 40px;
		width: 40px;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.button-cancel svg {
		width: 15px;
		fill: #eee;
	}

	.button-cancel:hover {
		background: #ff3636;
	}

	.button-cancel:hover .text {
		color: transparent;
	}

	.button-cancel:hover .icon {
		width: 150px;
		border-left: none;
		transform: translateX(0);
	}

	.button-cancel:focus {
		outline: none;
	}

	.button-cancel:active .icon svg {
		transform: scale(0.8);
	}

	.button-done {
		margin-left: 2rem;
		background: #60ae60;
	}

	.button-done .icon {
		border-left: 1px solid #379449;
	}

	.button-done:hover {
		background: #60ae60;
	}

	.modal input,
	.modal textarea {
		margin: 0;
		padding: 15px 10px;
		font-size: 15px;
		font-family: Arial, Helvetica, sans-serif;
		border: #cccccc solid 2px;
		border-radius: 5px;
		width: 500px;
	}

	.link-box {
		display: flex;
		height: 50px;
		width: 500px;
		border: #cccccc solid 2px;
		border-radius: 5px;
		margin: 20px 0;
		position: relative;
		/* To position ::before correctly */
	}

	.link-box input {
		width: calc(100% - 50px);
		border: none;
		margin: 0;
	}

	.link-box button {
		display: flex;
		justify-content: center;
		align-items: center;
		padding: 0;
		width: 50px;
		border: none;
		background: #cccccc;
		/* border-left: #CCCCCC solid 2px; */
		transition: background 0.3s;
	}

	.link-box button:hover {
		background: transparent;
		cursor: pointer;
	}

	.link-box p {
		content: "Link Copied!";
		font-family: "kiwi-maru";
		position: absolute;
		left: calc(100% + 10px);
		height: 100%;
		text-wrap: nowrap;
		display: flex;
		align-items: center;
		opacity: 0;
		margin: 0;
	}

	.container {
		position: absolute;
		top: 0;
		left: 0;
		right: 0;
		bottom: 0;
		width: 100%;
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 1.5rem;
	}

	.modal {
		display: flex;
		flex-direction: column;
		width: 100%;
		max-width: 700px;
		height: 60%;
		background-color: #fff;
		border-color: rgb(102, 121, 228);
		box-shadow: 0 15px 30px 0 rgba(98, 174, 202, 0.15);
		border-radius: 10px;
		color: rgb(16, 27, 90);
	}

	.modal__header {
		padding: 1rem 1.5rem;
		border-bottom: 1px solid #ddd;
		display: flex;
		align-items: center;
		justify-content: space-between;
	}

	.modal__body {
		padding: 1rem 1rem;
		overflow-y: auto;
	}

	.modal__footer {
		display: flex;
		flex-direction: row;
		padding: 0 1.5rem 1.5rem;
	}

	.modal__title {
		font-weight: 700;
		font-size: 1.25rem;
	}

	.button {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		transition: 0.15s ease;
	}

	.button--icon {
		width: 2.5rem;
		height: 2.5rem;
		background-color: transparent;
		border-radius: 0.25rem;
	}

	.button--icon:focus,
	.button--icon:hover {
		background-color: #ededed;
	}

	.button--primary {
		background-color: #007dab;
		color: #fff;
		padding: 0.75rem 1.25rem;
		border-radius: 0.25rem;
		font-weight: 500;
		font-size: 0.875rem;
	}

	.button--primary:hover {
		background-color: #006489;
	}

	::-webkit-scrollbar-thumb {
		background: var(--avatair-blue);
		border-radius: 6px;
	}

	::-webkit-scrollbar {
		width: 20px;
	}

	::-webkit-scrollbar-track {
		background: transparent;
	}
</style>
