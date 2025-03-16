import React, { useState, useEffect } from 'react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const BetaDistribution = () => {

    const alphaDefault = 4 // Replace 4 with the estimated alpha parameter from the BinaryPredictor agent
    const betaDefault = 5 // Replace 5 with the estimated beta parameter from the BinaryPredictor agent

    // Using the specified parameters with state for adjustments
    const [alpha, setAlpha] = useState(alphaDefault);
    const [beta, setBeta] = useState(betaDefault);
    const [sampleSize, setSampleSize] = useState(1000);
    const [samples, setSamples] = useState([]);
    const [histogramData, setHistogramData] = useState([]);

    // Function to generate beta distribution PDF values
    const generateBetaDistribution = (a, b) => {
    const points = [];
    // B(a,b) = gamma(a) * gamma(b) / gamma(a+b)
    // We'll use an approximation for this demo
    const betaFunction = (a, b) => {
      // This is a simple approximation
      return Math.exp((a-0.5)*Math.log(a) + (b-0.5)*Math.log(b) - (a+b-0.5)*Math.log(a+b) - 0.5*Math.log(2*Math.PI));
    };

    const betaCoeff = 1 / betaFunction(a, b);

    for (let x = 0.01; x <= 0.99; x += 0.01) {
      const density = betaCoeff * Math.pow(x, a-1) * Math.pow(1-x, b-1);
      points.push({
        x: x.toFixed(2),
        pdf: density
      });
    }
    return points;
    };

    // Function to sample from beta distribution using rejection sampling
    const generateBetaSamples = (a, b, numSamples) => {
    // This is a simplified approach for demonstration
    // In real applications, you'd use a proper beta sampling algorithm

    // Generate samples using an approximation method
    const samples = [];

    for (let i = 0; i < numSamples; i++) {
      // Use the fact that if X ~ Gamma(a) and Y ~ Gamma(b), then X/(X+Y) ~ Beta(a,b)
      // We'll use a simple approximation of Gamma sampling
      let x = 0;
      for (let j = 0; j < Math.floor(a); j++) {
        x -= Math.log(Math.random());
      }
      // Handle the fractional part
      if (a % 1 > 0) {
        x -= Math.log(Math.random()) * (a % 1);
      }

      let y = 0;
      for (let j = 0; j < Math.floor(b); j++) {
        y -= Math.log(Math.random());
      }
      // Handle the fractional part
      if (b % 1 > 0) {
        y -= Math.log(Math.random()) * (b % 1);
      }

      const betaSample = x / (x + y);
      samples.push(betaSample);
    }

    return samples;
    };

    // Create histogram bins
    const createHistogram = (samples, bins = 20) => {
    const min = 0;
    const max = 1;
    const binWidth = (max - min) / bins;

    // Initialize bins
    const histogram = Array(bins).fill(0).map((_, i) => ({
      binStart: (min + i * binWidth).toFixed(2),
      binEnd: (min + (i + 1) * binWidth).toFixed(2),
      count: 0
    }));

    // Count samples in each bin
    samples.forEach(sample => {
      if (sample >= min && sample < max) {
        const binIndex = Math.min(Math.floor((sample - min) / binWidth), bins - 1);
        histogram[binIndex].count += 1;
      }
    });

    // Convert counts to density for comparison with PDF
    const totalSamples = samples.length;
    histogram.forEach(bin => {
      bin.density = totalSamples > 0 ? bin.count / (totalSamples * binWidth) : 0;
    });

    return histogram;
    };

    // Calculate sample statistics
    const calculateSampleStats = (samples) => {
    if (samples.length === 0) return { mean: 0, stdDev: 0 };

    const mean = samples.reduce((sum, val) => sum + val, 0) / samples.length;

    const sumSquaredDiff = samples.reduce((sum, val) => {
      const diff = val - mean;
      return sum + diff * diff;
    }, 0);

    const variance = sumSquaredDiff / samples.length;
    const stdDev = Math.sqrt(variance);

    return { mean, stdDev };
    };

    // Generate new samples when parameters change
    useEffect(() => {
    const newSamples = generateBetaSamples(alpha, beta, sampleSize);
    setSamples(newSamples);
    setHistogramData(createHistogram(newSamples));
    }, [sampleSize, alpha, beta]);

    // Generate the theoretical PDF
    const theoreticalData = generateBetaDistribution(alpha, beta);

    // Handle parameter changes
    const handleAlphaChange = (e) => {
    const newAlpha = parseFloat(e.target.value);
    if (!isNaN(newAlpha) && newAlpha > 0) {
      setAlpha(newAlpha);
    }
    };

    const handleBetaChange = (e) => {
    const newBeta = parseFloat(e.target.value);
    if (!isNaN(newBeta) && newBeta > 0) {
      setBeta(newBeta);
    }
    };

    const handleSampleSizeChange = (e) => {
    const newSize = parseInt(e.target.value);
    if (!isNaN(newSize) && newSize > 0 && newSize <= 10000) {
      setSampleSize(newSize);
    }
    };

    // Regenerate samples with same size (for random variation)
    const handleRegenerateSamples = () => {
    const newSamples = generateBetaSamples(alpha, beta, sampleSize);
    setSamples(newSamples);
    setHistogramData(createHistogram(newSamples));
    };

    // Calculate mean and variance for this beta distribution
    const mean = alpha / (alpha + beta);
    const variance = (alpha * beta) / ((alpha + beta)**2 * (alpha + beta + 1));
    const stdDev = Math.sqrt(variance);
    const mode = alpha > 1 && beta > 1 ? (alpha - 1)/(alpha + beta - 2) : (alpha < 1 && beta >= 1 ? 0 : (alpha >= 1 && beta < 1 ? 1 : "Not unique"));

    // Calculate sample statistics
    const sampleStats = calculateSampleStats(samples);

    return (
    <div className="p-4 bg-white rounded-lg shadow-md">
      <h2 className="text-xl font-bold mb-4">Interactive Beta Distribution Explorer</h2>

      <div className="mb-4 grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label className="block mb-1 font-medium">Alpha (α):</label>
          <input
            type="number"
            min="0.1"
            step="0.1"
            value={alpha}
            onChange={handleAlphaChange}
            className="w-full px-2 py-1 border rounded"
          />
        </div>

        <div>
          <label className="block mb-1 font-medium">Beta (β):</label>
          <input
            type="number"
            min="0.1"
            step="0.1"
            value={beta}
            onChange={handleBetaChange}
            className="w-full px-2 py-1 border rounded"
          />
        </div>

        <div>
          <label className="block mb-1 font-medium">Sample Size:</label>
          <div className="flex items-center">
            <input
              type="number"
              min="10"
              max="10000"
              value={sampleSize}
              onChange={handleSampleSizeChange}
              className="w-full px-2 py-1 border rounded mr-2"
            />
            <button
              onClick={handleRegenerateSamples}
              className="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600"
            >
              Regenerate
            </button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-gray-50 p-2 rounded">
          <h3 className="text-lg font-semibold mb-2">Theoretical Beta(α={alpha.toFixed(4)}, β={beta.toFixed(4)})</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={theoreticalData} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
              <CartesianGrid stroke="#ccc" strokeDasharray="5 5" />
              <XAxis dataKey="x" label={{ value: 'x', position: 'bottom' }} />
              <YAxis label={{ value: 'Probability Density', angle: -90, position: 'left' }} />
              <Tooltip />
              <Line
                type="monotone"
                dataKey="pdf"
                stroke="#8884d8"
                strokeWidth={2}
                dot={false}
                name="PDF"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-gray-50 p-2 rounded">
          <h3 className="text-lg font-semibold mb-2">Empirical Distribution ({sampleSize} samples)</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={histogramData} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
              <CartesianGrid stroke="#ccc" strokeDasharray="5 5" />
              <XAxis
                dataKey="binStart"
                label={{ value: 'x', position: 'bottom' }}
              />
              <YAxis label={{ value: 'Density', angle: -90, position: 'left' }} />
              <Tooltip
                content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    const data = payload[0].payload;
                    return (
                      <div className="bg-white p-2 border border-gray-300 rounded">
                        <p>{`Range: ${data.binStart} - ${data.binEnd}`}</p>
                        <p>{`Count: ${data.count}`}</p>
                        <p>{`Density: ${data.density.toFixed(2)}`}</p>
                      </div>
                    );
                  }
                  return null;
                }}
              />
              <Bar dataKey="density" fill="#82ca9d" name="Samples" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="mt-4 text-sm text-gray-600">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <p><strong>Theoretical Properties:</strong></p>
            <ul className="list-disc pl-5">
              <li>Parameters: α = {alpha.toFixed(4)}, β = {beta.toFixed(4)}</li>
              <li>Mean = {mean.toFixed(4)}</li>
              <li>Standard Deviation = {stdDev.toFixed(4)}</li>
              <li>Variance = {variance.toFixed(6)}</li>
              <li>Mode = {typeof mode === 'number' ? mode.toFixed(4) : mode}</li>
            </ul>
          </div>
          <div>
            <p><strong>Empirical Properties:</strong></p>
            <ul className="list-disc pl-5">
              <li>Sample Size = {sampleSize}</li>
              <li>Sample Mean = {sampleStats.mean.toFixed(4)}</li>
              <li>Sample Std Dev = {sampleStats.stdDev.toFixed(4)}</li>
              <li>Difference from Theoretical:
                <ul className="list-disc pl-5 mt-1">
                  <li>Mean: {(Math.abs(sampleStats.mean - mean) / mean * 100).toFixed(2)}%</li>
                  <li>Std Dev: {(Math.abs(sampleStats.stdDev - stdDev) / stdDev * 100).toFixed(2)}%</li>
                </ul>
              </li>
            </ul>
          </div>
        </div>
        <div className="mt-2">
          <p><strong>Distribution Shape:</strong>
            {alpha < 1 && beta < 1 ? " U-shaped" :
             alpha <= 1 && beta > 1 ? " J-shaped, decreasing" :
             alpha > 1 && beta <= 1 ? " J-shaped, increasing" :
             alpha === 1 && beta === 1 ? " Uniform" :
             alpha === beta ? " Symmetric, bell-shaped" :
             alpha < beta ? " Skewed left" : " Skewed right"}
          </p>
          <p className="mt-1">Note: The empirical distribution uses random sampling and will vary with each regeneration.</p>
        </div>
      </div>
    </div>
    );
};

export default BetaDistribution;