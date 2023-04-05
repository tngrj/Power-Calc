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

	function powerConsump(data) {
		const periodInfoDiv = document.getElementById('power_consumption_div');
		for (let i = 0; i < data.period_info.length; i++) {
			console.log('ran', i);
			const periodInfo = document.createElement('p');
			periodInfo.textContent = data.period_info[i];
			periodInfoDiv.appendChild(periodInfo);
		}
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

		var e = document.getElementById('applianceSelect');
		var selectedValue = e.options[e.selectedIndex].text;

		let url;
		if (selectedValue === 'Air Conditioner') {
			url = '/aircon';
		} else if (selectedValue === 'Oven') {
			url = '/oven';
		} else if (selectedValue === 'Heater') {
			url = '/heater';
		} else {
			alert('Please select an appliance.');
			return;
		}

		const response = await fetch(url, {
			method: 'POST',
			body: formData,
		});

		if (response.ok) {
			const data = await response.json();
			createGraph(data);
			powerConsump(data);
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

<div id="uploadContainer" class="container">
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

	<div class="is-flex is-justify-content-center">
		<div class="field has-addons">
			<p class="control has-icons-left">
				<span class="select is-medium">
					<select id="applianceSelect">
						<option value="" disabled selected>Select Appliance</option>
						<option>Air Conditioner</option>
						<option>Oven</option>
						<option>Heater</option>
					</select>
				</span>
				<span class="icon is-left">
					<i class="fa-solid fa-gear" />
				</span>
			</p>
			<p class="control">
				<button class="button is-primary is-medium" on:click={submitFile}>Submit</button>
			</p>
		</div>
	</div>
</div>

<div class="container" id="graphContainer" style="display: none">
	<canvas bind:this={portfolio} />
	<br />
	<div class="content is-medium has-text-centered"><p id="power_consumption_div" /></div>
</div>
