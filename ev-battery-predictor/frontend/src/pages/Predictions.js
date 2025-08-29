import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Row, 
  Col, 
  Select, 
  Button, 
  Typography, 
  Alert,
  Statistic, 
  Table,
  Divider,
  Tag,
  Space
} from 'antd';
import { 
  LineChartOutlined, 
  WarningOutlined, 
  InfoCircleOutlined,
  RocketOutlined
} from '@ant-design/icons';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine
} from 'recharts';
import { vehicleAPI, modelAPI, predictionAPI } from '../services/api';

const { Title, Text } = Typography;
const { Option } = Select;

const Predictions = () => {
  const [loading, setLoading] = useState(false);
  const [vehicles, setVehicles] = useState([]);
  const [models, setModels] = useState([]);
  const [selectedVehicle, setSelectedVehicle] = useState(null);
  const [selectedModel, setSelectedModel] = useState(null);
  const [forecast, setForecast] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    loadVehicles();
  }, []);

  useEffect(() => {
    if (selectedVehicle) {
      loadModels(selectedVehicle);
    }
  }, [selectedVehicle]);

  const loadVehicles = async () => {
    try {
      const response = await vehicleAPI.getVehicles();
      setVehicles(response.data);
      if (response.data.length > 0) {
        setSelectedVehicle(response.data[0].id);
      }
    } catch (err) {
      setError('Failed to load vehicles');
      console.error('Error loading vehicles:', err);
    }
  };

  const loadModels = async (vehicleId) => {
    try {
      const response = await modelAPI.getModels(vehicleId);
      const trainedModels = response.data.filter(model => model.is_trained);
      setModels(trainedModels);
      setSelectedModel(null);
      setForecast(null);
      setMetrics(null);
    } catch (err) {
      setError('Failed to load models');
      console.error('Error loading models:', err);
    }
  };

  const generateForecast = async () => {
    if (!selectedModel) return;

    setLoading(true);
    setError('');
    
    try {
      // Generate SOH forecast
      const forecastResponse = await predictionAPI.getSOHForecast({
        model_id: selectedModel,
        prediction_steps: 730, // 2 years
        time_step_days: 7 // Weekly predictions
      });

      // Get model metrics
      const metricsResponse = await predictionAPI.getModelMetrics(selectedModel);

      setForecast(forecastResponse.data);
      setMetrics(metricsResponse.data);
    } catch (err) {
      setError('Failed to generate forecast');
      console.error('Error generating forecast:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatChartData = (forecast) => {
    if (!forecast) return [];
    
    return forecast.predictions.map((soh, index) => ({
      date: forecast.timestamps[index],
      soh: soh,
      timestamp: new Date(forecast.timestamps[index]).toLocaleDateString()
    }));
  };

  const getThresholdInfo = (crossings) => {
    const thresholds = ['70%', '50%', '20%'];
    return thresholds.map(threshold => {
      const crossing = crossings[threshold];
      return {
        threshold,
        crossed: !!crossing,
        date: crossing ? new Date(crossing.timestamp).toLocaleDateString() : null,
        daysFromNow: crossing ? crossing.days_from_start : null,
        soh: crossing ? crossing.soh.toFixed(1) : null
      };
    });
  };

  const getMetricsColumns = () => [
    {
      title: 'Metric',
      dataIndex: 'metric',
      key: 'metric',
    },
    {
      title: 'Value',
      dataIndex: 'value',
      key: 'value',
      render: (value) => typeof value === 'number' ? value.toFixed(4) : value || 'N/A'
    },
    {
      title: 'Description',
      dataIndex: 'description',
      key: 'description',
    }
  ];

  const getMetricsData = (metrics) => {
    if (!metrics) return [];
    
    return [
      {
        key: '1',
        metric: 'R² Score',
        value: metrics.r2_score,
        description: 'Coefficient of determination (higher is better, max 1.0)'
      },
      {
        key: '2', 
        metric: 'RMSE',
        value: metrics.rmse,
        description: 'Root Mean Square Error (lower is better)'
      },
      {
        key: '3',
        metric: 'MAE', 
        value: metrics.mae,
        description: 'Mean Absolute Error (lower is better)'
      },
      {
        key: '4',
        metric: 'MAPE (%)',
        value: metrics.mape,
        description: 'Mean Absolute Percentage Error (lower is better)'
      }
    ];
  };

  return (
    <div>
      <Title level={2}>
        <LineChartOutlined /> SOH Predictions & Forecasting
      </Title>
      
      {error && (
        <Alert
          message={error}
          type="error"
          showIcon
          style={{ marginBottom: 24 }}
        />
      )}

      <Card title="Prediction Configuration" style={{ marginBottom: 24 }}>
        <Row gutter={16}>
          <Col xs={24} sm={8}>
            <Text strong>Select Vehicle:</Text>
            <Select
              style={{ width: '100%', marginTop: 8 }}
              placeholder="Choose a vehicle"
              value={selectedVehicle}
              onChange={setSelectedVehicle}
            >
              {vehicles.map(vehicle => (
                <Option key={vehicle.id} value={vehicle.id}>
                  {vehicle.make} {vehicle.model} ({vehicle.year})
                </Option>
              ))}
            </Select>
          </Col>
          
          <Col xs={24} sm={8}>
            <Text strong>Select Trained Model:</Text>
            <Select
              style={{ width: '100%', marginTop: 8 }}
              placeholder="Choose a model"
              value={selectedModel}
              onChange={setSelectedModel}
              disabled={!selectedVehicle}
            >
              {models.map(model => (
                <Option key={model.id} value={model.id}>
                  {model.name} ({model.model_type})
                  <Tag color="green" style={{ marginLeft: 8 }}>
                    R²: {model.test_score?.toFixed(3) || 'N/A'}
                  </Tag>
                </Option>
              ))}
            </Select>
          </Col>
          
          <Col xs={24} sm={8}>
            <div style={{ marginTop: 32 }}>
              <Button
                type="primary"
                icon={<RocketOutlined />}
                onClick={generateForecast}
                disabled={!selectedModel}
                loading={loading}
                size="large"
              >
                Generate Forecast
              </Button>
            </div>
          </Col>
        </Row>
      </Card>

      {forecast && (
        <>
          {/* Summary Statistics */}
          <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
            <Col xs={24} sm={6}>
              <Card>
                <Statistic
                  title="Current SOH"
                  value={forecast.current_soh}
                  suffix="%"
                  precision={1}
                  valueStyle={{ color: forecast.current_soh > 80 ? '#52c41a' : forecast.current_soh > 50 ? '#fa8c16' : '#f5222d' }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={6}>
              <Card>
                <Statistic
                  title="Forecast Days"
                  value={forecast.total_forecast_days}
                  suffix="days"
                  valueStyle={{ color: '#1890ff' }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={6}>
              <Card>
                <Statistic
                  title="Data Points"
                  value={forecast.prediction_steps}
                  valueStyle={{ color: '#722ed1' }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={6}>
              <Card>
                <Statistic
                  title="Time Step"
                  value={forecast.time_step_days}
                  suffix="days"
                  valueStyle={{ color: '#13c2c2' }}
                />
              </Card>
            </Col>
          </Row>

          {/* Main Forecast Chart */}
          <Card title="SOH Forecast Until 20%" style={{ marginBottom: 24 }}>
            <ResponsiveContainer width="100%" height={400}>
              <LineChart data={formatChartData(forecast)}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="timestamp" 
                  tick={{ fontSize: 12 }}
                  interval="preserveStartEnd"
                />
                <YAxis 
                  domain={[0, 100]}
                  label={{ value: 'SOH (%)', angle: -90, position: 'insideLeft' }}
                />
                <Tooltip 
                  formatter={(value, name) => [`${value.toFixed(1)}%`, 'SOH']}
                  labelFormatter={(label) => `Date: ${label}`}
                />
                <Legend />
                
                {/* Threshold lines */}
                <ReferenceLine y={70} stroke="#fa8c16" strokeDasharray="5 5" label="70% Critical" />
                <ReferenceLine y={50} stroke="#f5222d" strokeDasharray="5 5" label="50% Warning" />
                <ReferenceLine y={20} stroke="#ff4d4f" strokeWidth={2} label="20% End of Life" />
                
                <Line
                  type="monotone"
                  dataKey="soh"
                  stroke="#1890ff"
                  strokeWidth={2}
                  dot={false}
                  activeDot={{ r: 6 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </Card>

          {/* Threshold Crossings */}
          <Card 
            title={
              <Space>
                <WarningOutlined />
                Threshold Crossings Analysis
              </Space>
            } 
            style={{ marginBottom: 24 }}
          >
            <Row gutter={[16, 16]}>
              {getThresholdInfo(forecast.threshold_crossings).map((threshold, index) => (
                <Col xs={24} sm={8} key={index}>
                  <Card size="small" style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: '18px', fontWeight: 'bold', color: threshold.crossed ? '#f5222d' : '#52c41a' }}>
                      {threshold.threshold} Threshold
                    </div>
                    <Divider style={{ margin: '12px 0' }} />
                    {threshold.crossed ? (
                      <>
                        <div><Text strong>Crossing Date:</Text> {threshold.date}</div>
                        <div><Text strong>Days from Now:</Text> {threshold.daysFromNow}</div>
                        <div><Text strong>SOH at Crossing:</Text> {threshold.soh}%</div>
                        <Tag color="red" style={{ marginTop: 8 }}>WILL CROSS</Tag>
                      </>
                    ) : (
                      <>
                        <div style={{ color: '#52c41a' }}>
                          <InfoCircleOutlined /> Not reached in forecast period
                        </div>
                        <Tag color="green" style={{ marginTop: 8 }}>SAFE</Tag>
                      </>
                    )}
                  </Card>
                </Col>
              ))}
            </Row>
          </Card>
        </>
      )}

      {/* Model Performance Metrics */}
      {metrics && (
        <Card title="Model Performance Metrics" style={{ marginBottom: 24 }}>
          <Table
            columns={getMetricsColumns()}
            dataSource={getMetricsData(metrics)}
            pagination={false}
            size="small"
          />
        </Card>
      )}

      {/* Instructions */}
      {!forecast && (
        <Card>
          <Alert
            message="Get Started with SOH Forecasting"
            description={
              <div>
                <p>To generate battery health predictions:</p>
                <ol>
                  <li>Select a vehicle from your fleet</li>
                  <li>Choose a trained ML model</li>
                  <li>Click "Generate Forecast" to see SOH predictions until 20% threshold</li>
                </ol>
                <p>The forecast will show you:</p>
                <ul>
                  <li>Future SOH trends over time</li>
                  <li>When the battery will cross 70%, 50%, and 20% thresholds</li>
                  <li>Model performance metrics for confidence assessment</li>
                </ul>
              </div>
            }
            type="info"
            showIcon
          />
        </Card>
      )}
    </div>
  );
};

export default Predictions;