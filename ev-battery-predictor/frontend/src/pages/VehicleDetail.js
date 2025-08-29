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
  message,
  Popconfirm
} from 'antd';
import {
  ArrowLeftOutlined,
  EditOutlined,
  DeleteOutlined,
  PlusOutlined,
  ExperimentOutlined
} from '@ant-design/icons';
import { vehicleAPI, batteryDataAPI, modelAPI } from '../services/api';
import { handleApiError } from '../utils/errorHandling';
import BatteryHealthChart from '../components/BatteryHealthChart';

const { Title } = Typography;

const VehicleDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [vehicle, setVehicle] = useState(null);
  const [batteryData, setBatteryData] = useState([]);
  const [models, setModels] = useState([]);
  const [error, setError] = useState('');

  const loadVehicleDetails = useCallback(async () => {
    try {
      setLoading(true);
      setError('');

      // Load vehicle details
      const vehicleResponse = await vehicleAPI.getVehicle(id);
      setVehicle(vehicleResponse.data);

      // Load battery data
      const batteryResponse = await batteryDataAPI.getBatteryData(id);
      setBatteryData(batteryResponse.data);

      // Load ML models
      const modelsResponse = await modelAPI.getModels(id);
      setModels(modelsResponse.data);

    } catch (error) {
      const errorMsg = handleApiError(error, 'Failed to load vehicle details');
      setError(errorMsg.error);
      message.error(errorMsg.error);
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    if (id) {
      loadVehicleDetails();
    }
  }, [id, loadVehicleDetails]);

  const handleDeleteVehicle = async () => {
    try {
      await vehicleAPI.deleteVehicle(id);
      message.success('Vehicle deleted successfully');
      navigate('/vehicles');
    } catch (error) {
      const errorMsg = handleApiError(error, 'Failed to delete vehicle');
      message.error(errorMsg.error);
    }
  };

  const batteryDataColumns = [
    {
      title: 'Date',
      dataIndex: 'measurement_timestamp',
      key: 'measurement_timestamp',
      render: (date) => new Date(date).toLocaleString(),
      sorter: (a, b) => new Date(a.measurement_timestamp) - new Date(b.measurement_timestamp),
    },
    {
      title: 'SOH (%)',
      dataIndex: 'state_of_health',
      key: 'state_of_health',
      render: (value) => (
        <Tag color={value >= 90 ? 'green' : value >= 80 ? 'orange' : 'red'}>
          {value}%
        </Tag>
      ),
      sorter: (a, b) => a.state_of_health - b.state_of_health,
    },
    {
      title: 'SOC (%)',
      dataIndex: 'state_of_charge',
      key: 'state_of_charge',
      render: (value) => value ? `${value}%` : 'N/A',
    },
    {
      title: 'Voltage (V)',
      dataIndex: 'voltage',
      key: 'voltage',
      render: (value) => value ? `${value}V` : 'N/A',
    },
    {
      title: 'Current (A)',
      dataIndex: 'current',
      key: 'current',
      render: (value) => value ? `${value}A` : 'N/A',
    },
    {
      title: 'Temperature (°C)',
      dataIndex: 'temperature',
      key: 'temperature',
      render: (value) => value ? `${value}°C` : 'N/A',
    },
    {
      title: 'Source',
      dataIndex: 'data_source',
      key: 'data_source',
      render: (source) => <Tag>{source || 'Manual'}</Tag>,
    },
  ];

  const modelsColumns = [
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: 'Type',
      dataIndex: 'model_type',
      key: 'model_type',
      render: (type) => <Tag color="blue">{type}</Tag>,
    },
    {
      title: 'Status',
      dataIndex: 'is_trained',
      key: 'is_trained',
      render: (trained) => (
        <Tag color={trained ? 'green' : 'orange'}>
          {trained ? 'Trained' : 'Not Trained'}
        </Tag>
      ),
    },
    {
      title: 'Training Score',
      dataIndex: 'training_score',
      key: 'training_score',
      render: (score) => score ? score.toFixed(3) : 'N/A',
    },
    {
      title: 'Test Score',
      dataIndex: 'test_score',
      key: 'test_score',
      render: (score) => score ? score.toFixed(3) : 'N/A',
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <Button
          type="primary"
          size="small"
          onClick={() => navigate(`/models/${record.id}`)}
        >
          View Details
        </Button>
      ),
    },
  ];

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
      </div>
    );
  }

  if (error || !vehicle) {
    return (
      <div>
        <Button 
          icon={<ArrowLeftOutlined />} 
          onClick={() => navigate('/vehicles')}
          style={{ marginBottom: 16 }}
        >
          Back to Vehicles
        </Button>
        <Alert
          message="Error Loading Vehicle"
          description={error || 'Vehicle not found'}
          type="error"
          showIcon
        />
      </div>
    );
  }

  const latestData = batteryData.length > 0 ? batteryData[0] : null;
  const healthyReadings = batteryData.filter(d => d.state_of_health >= 80).length;
  const warningReadings = batteryData.filter(d => d.state_of_health < 80).length;

  return (
    <div>
      <Row justify="space-between" align="middle" style={{ marginBottom: 24 }}>
        <Col>
          <Space>
            <Button 
              icon={<ArrowLeftOutlined />} 
              onClick={() => navigate('/vehicles')}
            >
              Back
            </Button>
            <Title level={2} style={{ margin: 0 }}>{vehicle.name}</Title>
          </Space>
        </Col>
        <Col>
          <Space>
            <Button
              icon={<PlusOutlined />}
              onClick={() => navigate('/data-upload')}
            >
              Add Data
            </Button>
            <Button
              icon={<ExperimentOutlined />}
              onClick={() => navigate('/models')}
            >
              Create Model
            </Button>
            <Button
              icon={<EditOutlined />}
              onClick={() => navigate('/vehicles')} // Would open edit modal
            >
              Edit
            </Button>
            <Popconfirm
              title="Delete Vehicle"
              description="Are you sure? This will delete all associated data and models."
              onConfirm={handleDeleteVehicle}
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

      {/* Vehicle Information */}
      <Card title="Vehicle Information" style={{ marginBottom: 24 }}>
        <Descriptions column={2}>
          <Descriptions.Item label="Make">{vehicle.make || 'Not specified'}</Descriptions.Item>
          <Descriptions.Item label="Model">{vehicle.model || 'Not specified'}</Descriptions.Item>
          <Descriptions.Item label="Year">{vehicle.year || 'Not specified'}</Descriptions.Item>
          <Descriptions.Item label="Battery Capacity">{vehicle.battery_capacity ? `${vehicle.battery_capacity} kWh` : 'Not specified'}</Descriptions.Item>
          <Descriptions.Item label="Battery Type">{vehicle.battery_type || 'Not specified'}</Descriptions.Item>
          <Descriptions.Item label="Created">{new Date(vehicle.created_at).toLocaleDateString()}</Descriptions.Item>
        </Descriptions>
      </Card>

      {/* Statistics */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Total Data Points"
              value={batteryData.length}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Latest SOH"
              value={latestData?.state_of_health || 0}
              suffix="%"
              valueStyle={{ color: latestData?.state_of_health >= 80 ? '#52c41a' : '#fa541c' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Healthy Readings"
              value={healthyReadings}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Warning Readings"
              value={warningReadings}
              valueStyle={{ color: '#fa541c' }}
            />
          </Card>
        </Col>
      </Row>

      {/* Battery Health Chart */}
      {batteryData.length > 0 && (
        <Card title="Battery Health Trends" style={{ marginBottom: 24 }}>
          <BatteryHealthChart data={batteryData} height={400} />
        </Card>
      )}

      {/* ML Models */}
      <Card title="ML Models" style={{ marginBottom: 24 }}>
        {models.length > 0 ? (
          <Table
            columns={modelsColumns}
            dataSource={models}
            rowKey="id"
            pagination={{ pageSize: 5 }}
          />
        ) : (
          <Alert
            message="No ML models found"
            description="Create your first machine learning model to start predicting battery health."
            type="info"
            showIcon
            action={
              <Button
                type="primary"
                icon={<ExperimentOutlined />}
                onClick={() => navigate('/models')}
              >
                Create Model
              </Button>
            }
          />
        )}
      </Card>

      {/* Battery Data */}
      <Card title="Battery Data History">
        {batteryData.length > 0 ? (
          <Table
            columns={batteryDataColumns}
            dataSource={batteryData}
            rowKey="id"
            pagination={{ pageSize: 10 }}
            scroll={{ x: 800 }}
          />
        ) : (
          <Alert
            message="No battery data found"
            description="Upload battery data to start monitoring the health of this vehicle."
            type="info"
            showIcon
            action={
              <Button
                type="primary"
                icon={<PlusOutlined />}
                onClick={() => navigate('/data-upload')}
              >
                Upload Data
              </Button>
            }
          />
        )}
      </Card>
    </div>
  );
};

export default VehicleDetail;