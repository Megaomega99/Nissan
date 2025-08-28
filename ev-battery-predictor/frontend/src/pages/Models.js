import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Row, 
  Col, 
  Button, 
  Typography, 
  Alert, 
  Table, 
  Tag, 
  Space, 
  Modal, 
  Form, 
  Input, 
  Select, 
  Progress,
  Tooltip,
  Popconfirm,
  message,
  Statistic
} from 'antd';
import { 
  ExperimentOutlined, 
  PlusOutlined, 
  PlayCircleOutlined,
  DeleteOutlined,
  InfoCircleOutlined,
  CheckCircleOutlined,
  LoadingOutlined
} from '@ant-design/icons';
import { vehicleAPI, modelAPI, predictionAPI } from '../services/api';

const { Title, Text } = Typography;
const { Option } = Select;

const Models = () => {
  const [loading, setLoading] = useState(false);
  const [vehicles, setVehicles] = useState([]);
  const [models, setModels] = useState([]);
  const [selectedVehicle, setSelectedVehicle] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showMetricsModal, setShowMetricsModal] = useState(false);
  const [selectedModelMetrics, setSelectedModelMetrics] = useState(null);
  const [trainingModel, setTrainingModel] = useState(null);
  const [error, setError] = useState('');
  const [form] = Form.useForm();

  const modelTypes = [
    { value: 'linear', label: 'Linear Regression', description: 'Simple linear relationship' },
    { value: 'polynomial', label: 'Polynomial Regression', description: 'Non-linear polynomial relationship' },
    { value: 'random_forest', label: 'Random Forest', description: 'Ensemble of decision trees' },
    { value: 'svm', label: 'Support Vector Machine', description: 'Complex boundary learning' },
    { value: 'sgd', label: 'Stochastic Gradient Descent', description: 'Efficient large-scale learning' },
    { value: 'neural_network', label: 'Neural Network (MLP)', description: 'Multi-layer perceptron' },
    { value: 'perceptron', label: 'Perceptron', description: 'Single layer neural network' },
    { value: 'rnn', label: 'RNN (LSTM)', description: 'Recurrent neural network with LSTM' },
    { value: 'gru', label: 'GRU', description: 'Gated Recurrent Unit for time series' }
  ];

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
      setLoading(true);
      const response = await modelAPI.getModels(vehicleId);
      setModels(response.data);
    } catch (err) {
      setError('Failed to load models');
      console.error('Error loading models:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateModel = async (values) => {
    try {
      await modelAPI.createModel({
        ...values,
        vehicle_id: selectedVehicle
      });
      message.success('Model created successfully');
      setShowCreateModal(false);
      form.resetFields();
      loadModels(selectedVehicle);
    } catch (err) {
      message.error('Failed to create model');
      console.error('Error creating model:', err);
    }
  };

  const handleTrainModel = async (modelId) => {
    try {
      setTrainingModel(modelId);
      await modelAPI.trainModel(modelId, { test_size: 0.2 });
      message.success('Training started! Check back in a few moments.');
      
      // Poll for training completion
      const pollInterval = setInterval(async () => {
        try {
          const response = await modelAPI.getModel(modelId);
          if (response.data.is_trained) {
            clearInterval(pollInterval);
            setTrainingModel(null);
            message.success('Model training completed!');
            loadModels(selectedVehicle);
          }
        } catch (err) {
          clearInterval(pollInterval);
          setTrainingModel(null);
          console.error('Error polling training status:', err);
        }
      }, 5000);

      // Stop polling after 5 minutes
      setTimeout(() => {
        clearInterval(pollInterval);
        setTrainingModel(null);
      }, 300000);

    } catch (err) {
      setTrainingModel(null);
      message.error('Failed to start training');
      console.error('Error training model:', err);
    }
  };

  const handleDeleteModel = async (modelId) => {
    try {
      await modelAPI.deleteModel(modelId);
      message.success('Model deleted successfully');
      loadModels(selectedVehicle);
    } catch (err) {
      message.error('Failed to delete model');
      console.error('Error deleting model:', err);
    }
  };

  const showModelMetrics = async (modelId) => {
    try {
      const response = await predictionAPI.getModelMetrics(modelId);
      setSelectedModelMetrics(response.data);
      setShowMetricsModal(true);
    } catch (err) {
      message.error('Failed to load model metrics');
      console.error('Error loading metrics:', err);
    }
  };

  const getModelTypeInfo = (type) => {
    return modelTypes.find(mt => mt.value === type) || { label: type, description: 'Unknown model type' };
  };

  const getStatusColor = (model) => {
    if (!model.is_trained) return 'orange';
    if (model.test_score > 0.8) return 'green';
    if (model.test_score > 0.6) return 'blue';
    return 'red';
  };

  const getStatusText = (model) => {
    if (!model.is_trained) return 'Not Trained';
    if (model.test_score > 0.8) return 'Excellent';
    if (model.test_score > 0.6) return 'Good';
    return 'Poor';
  };

  const columns = [
    {
      title: 'Model Name',
      dataIndex: 'name',
      key: 'name',
      render: (text, record) => (
        <Space>
          <Text strong>{text}</Text>
          {record.is_trained && <CheckCircleOutlined style={{ color: '#52c41a' }} />}
        </Space>
      )
    },
    {
      title: 'Type',
      dataIndex: 'model_type',
      key: 'model_type',
      render: (type) => {
        const info = getModelTypeInfo(type);
        return (
          <Tooltip title={info.description}>
            <Tag color="blue">{info.label}</Tag>
          </Tooltip>
        );
      }
    },
    {
      title: 'Status',
      key: 'status',
      render: (_, record) => (
        <Tag color={getStatusColor(record)}>
          {trainingModel === record.id ? (
            <Space>
              <LoadingOutlined />
              Training
            </Space>
          ) : getStatusText(record)}
        </Tag>
      )
    },
    {
      title: 'Performance',
      key: 'performance',
      render: (_, record) => (
        record.is_trained ? (
          <Space>
            <Text>R²: {record.test_score?.toFixed(3) || 'N/A'}</Text>
            {record.test_score && (
              <Progress
                type="circle"
                size="small"
                percent={Math.round(record.test_score * 100)}
                format={(percent) => `${percent}%`}
                strokeColor={record.test_score > 80 ? '#52c41a' : record.test_score > 60 ? '#1890ff' : '#f5222d'}
              />
            )}
          </Space>
        ) : (
          <Text type="secondary">Not available</Text>
        )
      )
    },
    {
      title: 'Created',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date) => new Date(date).toLocaleDateString()
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <Space>
          {!record.is_trained && (
            <Button
              type="primary"
              size="small"
              icon={<PlayCircleOutlined />}
              onClick={() => handleTrainModel(record.id)}
              loading={trainingModel === record.id}
            >
              Train
            </Button>
          )}
          {record.is_trained && (
            <Button
              size="small"
              icon={<InfoCircleOutlined />}
              onClick={() => showModelMetrics(record.id)}
            >
              Metrics
            </Button>
          )}
          <Popconfirm
            title="Are you sure you want to delete this model?"
            onConfirm={() => handleDeleteModel(record.id)}
            okText="Yes"
            cancelText="No"
          >
            <Button
              size="small"
              danger
              icon={<DeleteOutlined />}
            >
              Delete
            </Button>
          </Popconfirm>
        </Space>
      )
    }
  ];

  return (
    <div>
      <Title level={2}>
        <ExperimentOutlined /> ML Models
      </Title>
      
      {error && (
        <Alert
          message={error}
          type="error"
          showIcon
          style={{ marginBottom: 24 }}
        />
      )}

      <Card 
        title="Model Management" 
        extra={
          <Space>
            <Select
              style={{ width: 200 }}
              placeholder="Select vehicle"
              value={selectedVehicle}
              onChange={setSelectedVehicle}
            >
              {vehicles.map(vehicle => (
                <Option key={vehicle.id} value={vehicle.id}>
                  {vehicle.make} {vehicle.model} ({vehicle.year})
                </Option>
              ))}
            </Select>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => setShowCreateModal(true)}
              disabled={!selectedVehicle}
            >
              Create Model
            </Button>
          </Space>
        }
        style={{ marginBottom: 24 }}
      >
        <Table
          columns={columns}
          dataSource={models}
          loading={loading}
          rowKey="id"
          pagination={{ pageSize: 10 }}
        />
      </Card>

      {/* Create Model Modal */}
      <Modal
        title="Create New ML Model"
        open={showCreateModal}
        onCancel={() => {
          setShowCreateModal(false);
          form.resetFields();
        }}
        onOk={form.submit}
        okText="Create Model"
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleCreateModel}
        >
          <Form.Item
            name="name"
            label="Model Name"
            rules={[{ required: true, message: 'Please enter model name' }]}
          >
            <Input placeholder="e.g., Tesla Model S Linear Regression" />
          </Form.Item>

          <Form.Item
            name="model_type"
            label="Model Type"
            rules={[{ required: true, message: 'Please select model type' }]}
          >
            <Select placeholder="Select model algorithm">
              {modelTypes.map(type => (
                <Option key={type.value} value={type.value}>
                  <Space direction="vertical" size={0}>
                    <Text strong>{type.label}</Text>
                    <Text type="secondary" style={{ fontSize: '12px' }}>
                      {type.description}
                    </Text>
                  </Space>
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item
            name="description"
            label="Description (Optional)"
          >
            <Input.TextArea 
              rows={3} 
              placeholder="Describe the purpose or configuration of this model"
            />
          </Form.Item>
        </Form>
      </Modal>

      {/* Model Metrics Modal */}
      <Modal
        title="Model Performance Metrics"
        open={showMetricsModal}
        onCancel={() => setShowMetricsModal(false)}
        footer={null}
        width={600}
      >
        {selectedModelMetrics && (
          <div>
            <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
              <Col span={12}>
                <Card size="small">
                  <Statistic 
                    title="R² Score" 
                    value={selectedModelMetrics.r2_score} 
                    precision={4}
                    valueStyle={{ color: selectedModelMetrics.r2_score > 0.8 ? '#52c41a' : '#fa8c16' }}
                  />
                </Card>
              </Col>
              <Col span={12}>
                <Card size="small">
                  <Statistic 
                    title="RMSE" 
                    value={selectedModelMetrics.rmse} 
                    precision={4}
                    valueStyle={{ color: '#1890ff' }}
                  />
                </Card>
              </Col>
            </Row>
            
            <Row gutter={[16, 16]}>
              <Col span={12}>
                <Card size="small">
                  <Statistic 
                    title="MAE" 
                    value={selectedModelMetrics.mae} 
                    precision={4}
                    valueStyle={{ color: '#722ed1' }}
                  />
                </Card>
              </Col>
              <Col span={12}>
                <Card size="small">
                  <Statistic 
                    title="MAPE (%)" 
                    value={selectedModelMetrics.mape} 
                    precision={2}
                    valueStyle={{ color: '#13c2c2' }}
                  />
                </Card>
              </Col>
            </Row>

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
          </div>
        )}
      </Modal>
    </div>
  );
};

export default Models;