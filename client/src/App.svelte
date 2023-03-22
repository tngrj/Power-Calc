<script>
	import { onMount } from 'svelte';
	import Chart from 'chart.js/auto';
	import moment from 'moment';
	import 'chartjs-adapter-moment';

	let portfolio;

	async function getData() {
		const response = await fetch('./data');
		const data = await response.json();
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

	onMount(async () => {
		const { data, options } = await getData();
		const ctx = portfolio.getContext('2d');
		const myChart = new Chart(ctx, {
			type: 'line',
			data: data,
			options: options,
		});
	});
</script>

<!-- <script>
	import { onMount } from 'svelte';
	import Chart from 'chart.js/auto/auto.js';

	let portfolio;

	async function getData() {
		const response = await fetch('./test');
		const data = await response.json();
		return data;
	}

	function formatData(data) {
		const labels = data.map((_, i) => `Data point ${i + 1}`);
		return {
			labels,
			datasets: [
				{
					label: 'On Off state of appliance',
					data: data,
					fill: false,
					borderColor: 'rgb(75, 192, 192)',
					tension: 0.1,
				},
			],
		};
	}
	onMount(async () => {
		const data = await getData();
		const formattedData = formatData(data);
		const ctx = portfolio.getContext('2d');
		const myChart = new Chart(ctx, {
			type: 'line',
			data: formattedData,
		});
	});
</script>  -->

<canvas bind:this={portfolio} />

<div id="container">
	<div class="file-uploader">
		<img src="upload.png" alt="upload-icon" />
		<h2>Upload a dataset</h2>
		<input id="file-upload" type="file" />
		<label for="file-upload">Select Dataset</label>
	</div>
</div>
