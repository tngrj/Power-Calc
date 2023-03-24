<script>
	import Chart from 'chart.js/auto';
	import moment from 'moment';
	import 'chartjs-adapter-moment';

	let portfolio;

	async function getData(data) {
		const timestamps = data.timestamp.map((t) => moment(t, 'YYYY-MM-DD HH:mm:ss'));
		const power = data.power;
		const states = data.states;

		const chartData = {
			labels: timestamps,
			datasets: [
				{
					label: 'State',
					data: states,
					fill: false,
					borderColor: 'blue',
					yAxisID: 'state-axis',
				},
				{
					label: 'Power (W)',
					data: power,
					fill: false,
					borderColor: 'red',
					yAxisID: 'power-axis',
				},
			],
		};

		const chartOptions = {
			responsive: true,
			scales: {
				x: {
					type: 'time',
					time: {
						unit: 'minute',
						stepSize: 10,
						displayFormats: {
							minute: 'HH:mm',
						},
					},
					adapters: {
						date: {
							moment: moment,
						},
					},
				},
			},
		};

		return { data: chartData, options: chartOptions };
	}

	async function createGraph(dataParam) {
		const { data, options } = await getData(dataParam);
		const ctx = portfolio.getContext('2d');
		const myChart = new Chart(ctx, {
			type: 'line',
			data: data,
			options: options,
		});
	}

	async function submitFile() {
		const container = document.getElementById('uploadContainer');
		container.style.display = 'none';

		const fileInput = document.querySelector('input[type=file]');
		const file = fileInput.files[0];

		if (file.type !== 'text/csv') {
			alert('Please select a CSV file.');
			return;
		}

		const formData = new FormData();
		formData.append('file', file);

		console.log('this ran?');
		const response = await fetch('/data', {
			method: 'POST',
			body: formData,
		});

		if (response.ok) {
			const data = await response.json();
			createGraph(data);
		} else {
			alert('Error uploading file.');
		}

		const canvas = document.getElementById('graphContainer');
		canvas.style.display = 'block';
	}
</script>

<section class="hero">
	<div class="hero-body">
		<div class="container has-text-centered">
			<p class="title is-size-1-desktop has-text-weight-semibold">Power Calculator</p>
			<!-- <p class="subtitle is-size-3-desktop">Hero subtitle</p> -->
		</div>
	</div>
</section>

<div id="uploadContainer" class="container has-text-centered is-justify-content-center">
	<div id="uploadFile" class="file is-medium is-centered is-boxed has-name">
		<label class="file-label">
			<input class="file-input" type="file" name="resume" />
			<span class="file-cta">
				<span class="file-icon">
					<i class="fa-solid fa-arrow-up-from-bracket fa-bounce fa-lg" />
				</span>
				<span class="file-label"> Upload File </span>
			</span>
			<span class="file-name has-text-centered"> No file uploaded </span>
		</label>
	</div>

	<br />

	<div class="control">
		<button class="button is-info" on:click={submitFile}>Submit</button>
	</div>
</div>

<div class="container" id="graphContainer" style="display: none">
	<canvas bind:this={portfolio} />
</div>
