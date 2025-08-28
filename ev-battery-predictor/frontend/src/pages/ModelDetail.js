import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Typography,
  Card,
  Row,
  Col,
  Statistic,
  Button,
  Table,
  Tag,
  Space,
  Alert,
  Spin,
  Descriptions,
  Progress,
  message,
  Popconfirm,
  Tabs
} from 'antd';
import {
  ArrowLeftOutlined,
  EditOutlined,
  DeleteOutlined,
  PlayCircleOutlined,
  RocketOutlined
} from '@ant-design/icons';
import { modelAPI, predictionAPI, vehicleAPI } from '../services/api';
import { handleApiError } from '../utils/errorHandling';

const { Title, Text } = Typography;
const { TabPane } = Tabs;

const ModelDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [model, setModel] = useState(null);
  const [vehicle, setVehicle] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [predictionHistory, setPredictionHistory] = useState([]);
  const [trainingInProgress, setTrainingInProgress] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (id) {
      loadModelDetails();
    }
  }, [id, loadModelDetails]);

  const loadModelDetails = useCallback(async () => {
    try {
      setLoading(true);
      setError('');

      // Load model details
      const modelResponse = await modelAPI.getModel(id);
      setModel(modelResponse.data);

      // Load vehicle details
      const vehicleResponse = await vehicleAPI.getVehicle(modelResponse.data.vehicle_id);
      setVehicle(vehicleResponse.data);

      // Load metrics if model is trained
      if (modelResponse.data.is_trained) {
        try {
          const metricsResponse = await predictionAPI.getModelMetrics(id);
          setMetrics(metricsResponse.data);

          const historyResponse = await predictionAPI.getPredictionHistory(id);
          setPredictionHistory(historyResponse.data);
        } catch (err) {
          console.log('Metrics not available:', err);
        }
      }

    } catch (error) {
      const errorMsg = handleApiError(error, 'Failed to load model details');
      setError(errorMsg.error);
      message.error(errorMsg.error);
    } finally {
      setLoading(false);
    }
  }, [id]);

  const handleTrainModel = async () => {
    try {
      setTrainingInProgress(true);
      await modelAPI.trainModel(id, { test_size: 0.2 });
      message.success('Training started! Check back in a few moments.');
      
      // Poll for training completion
      const pollInterval = setInterval(async () => {
        try {
          const response = await modelAPI.getModel(id);
          if (response.data.is_trained) {
            clearInterval(pollInterval);
            setTrainingInProgress(false);
            message.success('Model training completed!');
            loadModelDetails();
          }
        } catch (err) {
          clearInterval(pollInterval);
          setTrainingInProgress(false);
          console.error('Error polling training status:', err);
        }
      }, 5000);

      // Stop polling after 5 minutes
      setTimeout(() => {
        clearInterval(pollInterval);
        setTrainingInProgress(false);
      }, 300000);

    } catch (err) {
      setTrainingInProgress(false);
      message.error('Failed to start training');
      console.error('Error training model:', err);
    }
  };

  const handleDeleteModel = async () => {
    try {
      await modelAPI.deleteModel(id);
      message.success('Model deleted successfully');
      navigate('/models');
    } catch (error) {
      const errorMsg = handleApiError(error, 'Failed to delete model');
      message.error(errorMsg.error);
    }
  };

  const getModelTypeInfo = (type) => {
    const modelTypes = {
      'linear': { label: 'Linear Regression', description: 'Simple linear relationship' },
      'polynomial': { label: 'Polynomial Regression', description: 'Non-linear polynomial relationship' },
      'random_forest': { label: 'Random Forest', description: 'Ensemble of decision trees' },
      'svm': { label: 'Support Vector Machine', description: 'Complex boundary learning' },
      'sgd': { label: 'Stochastic Gradient Descent', description: 'Efficient large-scale learning' },
      'neural_network': { label: 'Neural Network (MLP)', description: 'Multi-layer perceptron' },
      'perceptron': { label: 'Perceptron', description: 'Single layer neural network' },
      'rnn': { label: 'RNN (LSTM)', description: 'Recurrent neural network with LSTM' },
      'gru': { label: 'GRU', description: 'Gated Recurrent Unit for time series' }
    };
    return modelTypes[type] || { label: type, description: 'Unknown model type' };
  };

  const getPerformanceColor = (score) => {
    if (score > 0.8) return '#52c41a';
    if (score > 0.6) return '#1890ff';
    if (score > 0.4) return '#fa8c16';
    return '#f5222d';
  };

  const getMetricsData = () => {
    if (!metrics) return [];
    
    return [
      {
        key: '1',
        metric: 'R² Score',
        value: metrics.r2_score?.toFixed(4) || 'N/A',
        description: 'Coefficient of determination (higher is better, max 1.0)',
        color: getPerformanceColor(metrics.r2_score)
      },
      {
        key: '2', 
        metric: 'RMSE',
        value: metrics.rmse?.toFixed(4) || 'N/A',
        description: 'Root Mean Square Error (lower is better)',
        color: '#1890ff'
      },
      {
        key: '3',
        metric: 'MAE', 
        value: metrics.mae?.toFixed(4) || 'N/A',
        description: 'Mean Absolute Error (lower is better)',
        color: '#722ed1'
      },
      {
        key: '4',
        metric: 'MAPE (%)',
        value: metrics.mape?.toFixed(2) || 'N/A',
        description: 'Mean Absolute Percentage Error (lower is better)',
        color: '#13c2c2'
      }
    ];
  };

  const metricsColumns = [
    {
      title: 'Metric',
      dataIndex: 'metric',
      key: 'metric',
      render: (text, record) => (
        <Text strong style={{ color: record.color }}>{text}</Text>
      )
    },
    {
      title: 'Value',
      dataIndex: 'value',
      key: 'value',
      render: (value, record) => (
        <Tag color={record.color}>{value}</Tag>
      )
    },
    {
      title: 'Description',
      dataIndex: 'description',
      key: 'description',
    }
  ];

  const historyColumns = [
    {
      title: 'Date',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date) => new Date(date).toLocaleString(),
    },
    {
      title: 'Predicted SOH',
      dataIndex: 'predicted_soh',
      key: 'predicted_soh',
      render: (value) => `${value?.toFixed(1)}%`,
    },
    {
      title: 'Actual SOH',
      dataIndex: 'actual_soh',
      key: 'actual_soh',
      render: (value) => value ? `${value.toFixed(1)}%` : 'N/A',
    },
    {
      title: 'Error',
      key: 'error',
      render: (_, record) => {
        if (record.actual_soh && record.predicted_soh) {
          const error = Math.abs(record.actual_soh - record.predicted_soh);
          return (
            <Tag color={error < 2 ? 'green' : error < 5 ? 'orange' : 'red'}>
              {error.toFixed(1)}%
            </Tag>
          );
        }
        return 'N/A';
      }
    }
  ];

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
      </div>
    );
  }

  if (error || !model) {
    return (
      <div>
        <Button 
          icon={<ArrowLeftOutlined />} 
          onClick={() => navigate('/models')}
          style={{ marginBottom: 16 }}
        >
          Back to Models
        </Button>
        <Alert
          message="Error Loading Model"
          description={error || 'Model not found'}
          type="error"
          showIcon
        />
      </div>
    );
  }

  const modelTypeInfo = getModelTypeInfo(model.model_type);

  return (
    <div>
      <Row justify="space-between" align="middle" style={{ marginBottom: 24 }}>
        <Col>
          <Space>
            <Button 
              icon={<ArrowLeftOutlined />} 
              onClick={() => navigate('/models')}
            >
              Back
            </Button>
            <Title level={2} style={{ margin: 0 }}>{model.name}</Title>
            <Tag color={model.is_trained ? 'green' : 'orange'}>
              {trainingInProgress ? 'Training...' : (model.is_trained ? 'Trained' : 'Not Trained')}
            </Tag>
          </Space>
        </Col>
        <Col>
          <Space>
            {!model.is_trained && (
              <Button
                type="primary"
                icon={<PlayCircleOutlined />}
                onClick={handleTrainModel}
                loading={trainingInProgress}
              >
                Train Model
              </Button>
            )}
            {model.is_trained && (
              <Button
                icon={<RocketOutlined />}
                onClick={() => navigate('/predictions')}
              >
                Make Predictions
              </Button>
            )}
            <Button
              icon={<EditOutlined />}
              onClick={() => message.info('Edit functionality coming soon')}
            >
              Edit
            </Button>
            <Popconfirm
              title="Delete Model"
              description="Are you sure? This will delete all associated predictions."
              onConfirm={handleDeleteModel}
              okText="Yes"
              cancelText="No"
            >
              <Button danger icon={<DeleteOutlined />}>
                Delete
              </Button>
            </Popconfirm>
          </Space>
        </Col>
      </Row>

      {/* Model Information */}
      <Card title="Model Information" style={{ marginBottom: 24 }}>
        <Descriptions column={2}>
          <Descriptions.Item label="Name">{model.name}</Descriptions.Item>
          <Descriptions.Item label="Type">{modelTypeInfo.label}</Descriptions.Item>
          <Descriptions.Item label="Vehicle">{vehicle?.name || 'Unknown'}</Descriptions.Item>
          <Descriptions.Item label="Status">
            <Tag color={model.is_trained ? 'green' : 'orange'}>
              {trainingInProgress ? 'Training...' : (model.is_trained ? 'Trained' : 'Not Trained')}
            </Tag>
          </Descriptions.Item>
          <Descriptions.Item label="Created">{new Date(model.created_at).toLocaleString()}</Descriptions.Item>
          <Descriptions.Item label="Last Updated">{new Date(model.updated_at).toLocaleString()}</Descriptions.Item>
          <Descriptions.Item label="Description" span={2}>
            {model.description || 'No description provided'}
          </Descriptions.Item>
        </Descriptions>
      </Card>

      {model.is_trained && (
        <>
          {/* Performance Summary */}
          <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
            <Col xs={24} sm={12} lg={6}>
              <Card>
                <Statistic
                  title="Training Score"
                  value={model.training_score || 0}
                  precision={3}
                  valueStyle={{ color: getPerformanceColor(model.training_score) }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} lg={6}>
              <Card>
                <Statistic
                  title="Test Score"
                  value={model.test_score || 0}
                  precision={3}
                  valueStyle={{ color: getPerformanceColor(model.test_score) }}
                />
              </Card>
            </Col>
            <Col xs={24} sm={12} lg={6}>
              <Card>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: '14px', color: '#666' }}>Performance</div>
                  <Progress
                    type="circle"
                    percent={Math.round((model.test_score || 0) * 100)}
                    strokeColor={getPerformanceColor(model.test_score)}
                    size={60}
                  />
                </div>
              </Card>
            </Col>
            <Col xs={24} sm={12} lg={6}>
              <Card>
                <Statistic
                  title="Predictions Made"
                  value={predictionHistory.length}
                  valueStyle={{ color: '#1890ff' }}
                />
              </Card>
            </Col>
          </Row>

          {/* Detailed Analytics */}
          <Tabs defaultActiveKey="metrics">
            <TabPane tab="Performance Metrics" key="metrics">
              <Card>
                {metrics ? (
                  <>
                    <Table
                      columns={metricsColumns}
                      dataSource={getMetricsData()}
                      pagination={false}
                      size="small"
                    />
                    <Alert
                      message="Metric Interpretations"
                      description={
                        <ul style={{ margin: '8px 0' }}>
                          <li><strong>R² Score:</strong> Closer to 1.0 is better (explains variance)</li>
                          <li><strong>RMSE:</strong> Lower values indicate better predictions</li>
                          <li><strong>MAE:</strong> Average absolute error in predictions</li>
                          <li><strong>MAPE:</strong> Percentage error (lower is better)</li>
                        </ul>
                      }
                      type="info"
                      showIcon
                      style={{ marginTop: 16 }}
                    />
                  </>
                ) : (
                  <Alert
                    message="No metrics available"
                    description="Model metrics could not be loaded."
                    type="warning"
                    showIcon
                  />
                )}
              </Card>
            </TabPane>

            <TabPane tab="Prediction History" key="history">
              <Card>
                {predictionHistory.length > 0 ? (
                  <Table
                    columns={historyColumns}
                    dataSource={predictionHistory}
                    rowKey="id"
                    pagination={{ pageSize: 10 }}
                  />
                ) : (
                  <Alert
                    message="No prediction history"
                    description="No predictions have been made with this model yet."
                    type="info"
                    showIcon
                    action={
                      <Button
                        type="primary"
                        icon={<RocketOutlined />}
                        onClick={() => navigate('/predictions')}
                      >
                        Make Predictions
                      </Button>
                    }
                  />
                )}
              </Card>
            </TabPane>
          </Tabs>
        </>
      )}

      {!model.is_trained && (
        <Card>
          <Alert
            message="Model Not Trained"
            description={
              <div>
                <p>This model has not been trained yet. Training the model will:</p>
                <ul>
                  <li>Analyze the battery data for this vehicle</li>
                  <li>Learn patterns in battery health degradation</li>
                  <li>Generate performance metrics</li>
                  <li>Enable predictions and forecasting</li>
                </ul>
                <p>Click "Train Model" to start the training process.</p>
              </div>
            }
            type="info"
            showIcon
            action={
              <Button
                type="primary"
                icon={<PlayCircleOutlined />}
                onClick={handleTrainModel}
                loading={trainingInProgress}
                size="large"
              >
                Train Model
              </Button>
            }
          />
        </Card>
      )}
    </div>
  );
};

export default ModelDetail;