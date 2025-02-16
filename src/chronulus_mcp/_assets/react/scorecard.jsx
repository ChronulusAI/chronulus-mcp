import React from 'react';

const Scorecard = ({jsonData}) => {

  const totalScore = data.categories.reduce((sum, category) => sum + category.score, 0);
  const maxScore = data.categories.reduce((sum, category) => sum + category.max_score, 0);
  const highestScore = Math.max(...data.categories.map(category => category.score));

  return (
    <div className="max-w-full p-6 bg-white">
      <h3 className="text-2xl font-bold mb-4">Risk Assessment</h3>
      <h5 className="text-xl font-semibold mb-4 text-gray-700">
        Overall Score: {totalScore.toFixed(1)} / {maxScore.toFixed(1)} | Highest: {highestScore.toFixed(1)}
      </h5>

      <p className="mb-6 text-gray-800 leading-relaxed">
        {data.assessment}
      </p>

      <h3 className="text-2xl font-bold mb-4">Recommendations</h3>
      <p className="mb-6 text-gray-800 leading-relaxed">
        {data.recommendation}
      </p>

      <h3 className="text-2xl font-bold mb-4">Details</h3>
      <div className="overflow-x-auto">
        <table className="w-full border-collapse">
          <thead>
            <tr className="bg-gray-100">
              <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700 border-b">Risk Category</th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700 border-b">Score</th>
              <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700 border-b">Risk Factors</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {data.categories.map((category, index) => (
              <tr key={index} className="hover:bg-gray-50">
                <td className="px-6 py-4 text-sm font-medium text-gray-900">
                  {category.name}
                </td>
                <td className="px-6 py-4 text-sm text-gray-900">
                  {category.score.toFixed(1)} / {category.max_score.toFixed(1)}
                </td>
                <td className="px-6 py-4">
                  <ul className="list-disc pl-4 space-y-1 text-sm text-gray-700">
                    {category.risks.map((risk, riskIndex) => (
                      <li key={riskIndex}>{risk}</li>
                    ))}
                  </ul>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};


const Page = () => {

    const scorecardJson = {} // replace with the json-formatted scorecard from chronulus

    return (
        <Scorecard jsonData={scorecardJson} />
    );
};

export default Page;