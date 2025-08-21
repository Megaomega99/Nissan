import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import moment from 'moment';

const BatteryHealthChart = ({ data, height = 400 }) => {
  // Prepare data for chart
  const chartData = data
    .map(item => ({
      ...item,
      timestamp: moment(item.measurement_timestamp).format('MM/DD HH:mm'),
      date: new Date(item.measurement_timestamp).getTime()
    }))
    .sort((a, b) => a.date - b.date);

  const formatTooltip = (value, name) => {
    if (name === 'state_of_health') return [`${value}%`, 'State of Health'];
    if (name === 'voltage') return [`${value}V`, 'Voltage'];
    if (name === 'current') return [`${value}A`, 'Current'];
    if (name === 'temperature') return [`${value}°C`, 'Temperature'];
    return [value, name];
  };

  const formatLabel = (label) => {
    return `Time: ${label}`;
  };

  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={chartData}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis 
          dataKey="timestamp" 
          tick={{ fontSize: 12 }}
          interval="preserveStartEnd"
        />
        <YAxis 
          domain={['dataMin - 5', 'dataMax + 5']}
          tick={{ fontSize: 12 }}
        />
        <Tooltip 
          formatter={formatTooltip}
          labelFormatter={formatLabel}
          contentStyle={{
            backgroundColor: '#fff',
            border: '1px solid #ccc',
            borderRadius: '4px'
          }}
        />
        <Line 
          type="monotone" 
          dataKey="state_of_health" 
          stroke="#1890ff" 
          strokeWidth={2}
          dot={{ r: 4 }}
          activeDot={{ r: 6 }}
        />
        {data.some(d => d.voltage) && (
          <Line 
            type="monotone" 
            dataKey="voltage" 
            stroke="#52c41a" 
            strokeWidth={2}
            strokeDasharray="5 5"
            dot={{ r: 3 }}
          />
        )}
        {data.some(d => d.temperature) && (
          <Line 
            type="monotone" 
            dataKey="temperature" 
            stroke="#fa8c16" 
            strokeWidth={2}
            strokeDasharray="3 3"
            dot={{ r: 3 }}
          />
        )}
      </LineChart>
    </ResponsiveContainer>
  );
};

export default BatteryHealthChart;