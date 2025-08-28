import React, { useState, useEffect, useCallback } from 'react';
import {
  Typography,
  Card,
  Form,
  Input,
  InputNumber,
  DatePicker,
  Select,
  Button,
  Upload,
  Row,
  Col,
  Alert,
  message,
  Space,
  Table,
  Tag,
  Popconfirm
} from 'antd';
import {
  UploadOutlined,
  PlusOutlined,
  DeleteOutlined,
  DownloadOutlined,
  InboxOutlined
} from '@ant-design/icons';
import { vehicleAPI, batteryDataAPI } from '../services/api';
import { handleApiError } from '../utils/errorHandling';
import moment from 'moment';

const { Title } = Typography;
const { Dragger } = Upload;

const DataUpload = () => {
  const [vehicles, setVehicles] = useState([]);
  const [selectedVehicle, setSelectedVehicle] = useState(null);
  const [recentData, setRecentData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [uploadMode, setUploadMode] = useState('manual'); // 'manual' or 'file'
  const [form] = Form.useForm();

  useEffect(() => {
    loadVehicles();
  }, [loadVehicles]);

  useEffect(() => {
    if (selectedVehicle) {
      loadRecentData();
    }
  }, [selectedVehicle, loadRecentData]);

  const loadVehicles = useCallback(async () => {
    try {
      const response = await vehicleAPI.getVehicles();
      setVehicles(response.data);
      if (response.data.length > 0 && !selectedVehicle) {
        setSelectedVehicle(response.data[0].id);
      }
    } catch (error) {
      const errorMsg = handleApiError(error, 'Failed to load vehicles');
      message.error(errorMsg.error);
    }
  }, [selectedVehicle]);

  const loadRecentData = useCallback(async () => {
    try {
      const response = await batteryDataAPI.getBatteryData(selectedVehicle, { limit: 10 });
      setRecentData(response.data);
    } catch (error) {
      console.error('Failed to load recent data:', error);
    }
  }, [selectedVehicle]);

  const handleManualSubmit = async (values) => {
    try {
      setLoading(true);
      const dataToSubmit = {
        ...values,
        vehicle_id: selectedVehicle,
        measurement_timestamp: values.measurement_timestamp.toISOString(),
        data_source: 'Manual'
      };

      await batteryDataAPI.createBatteryData(dataToSubmit);
      message.success('Battery data added successfully');
      form.resetFields();
      loadRecentData();
    } catch (error) {
      const errorMsg = handleApiError(error, 'Failed to save battery data');
      message.error(errorMsg.error);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (file) => {
    if (!selectedVehicle) {
      message.error('Please select a vehicle first');
      return false;
    }

    try {
      setLoading(true);
      await batteryDataAPI.uploadBatteryData(selectedVehicle, file);
      message.success('File uploaded successfully');
      loadRecentData();
    } catch (error) {
      const errorMsg = handleApiError(error, 'Failed to upload file');
      message.error(errorMsg.error);
    } finally {
      setLoading(false);
    }
    
    return false; // Prevent default upload behavior
  };

  const handleDeleteData = async (id) => {
    try {
      await batteryDataAPI.deleteBatteryData(id);
      message.success('Data deleted successfully');
      loadRecentData();
    } catch (error) {
      const errorMsg = handleApiError(error, 'Failed to delete data');
      message.error(errorMsg.error);
    }
  };

  const downloadTemplate = () => {
    const csvContent = `state_of_health,state_of_charge,voltage,current,temperature,cycle_count,measurement_timestamp
95.5,85.0,420.1,15.5,25.0,150,2025-08-17T10:00:00Z
94.2,82.0,418.5,14.8,24.5,155,2025-08-16T10:00:00Z
93.1,80.0,416.2,14.2,24.0,160,2025-08-15T10:00:00Z`;
    
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'battery_data_template.csv';
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const dataColumns = [
    {
      title: 'Date',
      dataIndex: 'measurement_timestamp',
      key: 'measurement_timestamp',
      render: (date) => moment(date).format('MMM DD, YYYY HH:mm'),
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
      title: 'Source',
      dataIndex: 'data_source',
      key: 'data_source',
      render: (source) => <Tag>{source || 'Manual'}</Tag>,
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <Popconfirm
          title="Delete Data Point"
          description="Are you sure you want to delete this data point?"
          onConfirm={() => handleDeleteData(record.id)}
          okText="Yes"
          cancelText="No"
        >
          <Button danger size="small" icon={<DeleteOutlined />}>
            Delete
          </Button>
        </Popconfirm>
      ),
    },
  ];

  return (
    <div>
      <Title level={2}>Battery Data Upload</Title>
      
      {vehicles.length === 0 ? (
        <Alert
          message="No vehicles found"
          description="Please add a vehicle first before uploading battery data."
          type="warning"
          showIcon
          style={{ marginBottom: 24 }}
        />
      ) : (
        <>
          {/* Vehicle Selection */}
          <Card title="Select Vehicle" style={{ marginBottom: 24 }}>
            <Select
              style={{ width: '100%' }}
              placeholder="Select a vehicle"
              value={selectedVehicle}
              onChange={setSelectedVehicle}
              size="large"
            >
              {vehicles.map(vehicle => (
                <Select.Option key={vehicle.id} value={vehicle.id}>
                  {vehicle.name} ({vehicle.make} {vehicle.model})
                </Select.Option>
              ))}
            </Select>
          </Card>

          {selectedVehicle && (
            <>
              {/* Upload Mode Selection */}
              <Card title="Upload Method" style={{ marginBottom: 24 }}>
                <Space size="large">
                  <Button
                    type={uploadMode === 'manual' ? 'primary' : 'default'}
                    icon={<PlusOutlined />}
                    onClick={() => setUploadMode('manual')}
                  >
                    Manual Entry
                  </Button>
                  <Button
                    type={uploadMode === 'file' ? 'primary' : 'default'}
                    icon={<UploadOutlined />}
                    onClick={() => setUploadMode('file')}
                  >
                    File Upload
                  </Button>
                </Space>
              </Card>

              {/* Manual Entry Form */}
              {uploadMode === 'manual' && (
                <Card title="Manual Data Entry" style={{ marginBottom: 24 }}>
                  <Form
                    form={form}
                    layout="vertical"
                    onFinish={handleManualSubmit}
                    initialValues={{
                      measurement_timestamp: moment(),
                    }}
                  >
                    <Row gutter={16}>
                      <Col span={12}>
                        <Form.Item
                          name="state_of_health"
                          label="State of Health (%)"
                          rules={[
                            { required: true, message: 'Please enter SOH' },
                            { type: 'number', min: 0, max: 100, message: 'SOH must be between 0 and 100' },
                          ]}
                        >
                          <InputNumber
                            min={0}
                            max={100}
                            step={0.1}
                            placeholder="95.5"
                            style={{ width: '100%' }}
                            addonAfter="%"
                          />
                        </Form.Item>
                      </Col>
                      <Col span={12}>
                        <Form.Item
                          name="state_of_charge"
                          label="State of Charge (%)"
                        >
                          <InputNumber
                            min={0}
                            max={100}
                            step={0.1}
                            placeholder="85.0"
                            style={{ width: '100%' }}
                            addonAfter="%"
                          />
                        </Form.Item>
                      </Col>
                    </Row>

                    <Row gutter={16}>
                      <Col span={8}>
                        <Form.Item
                          name="voltage"
                          label="Voltage (V)"
                        >
                          <InputNumber
                            min={0}
                            step={0.1}
                            placeholder="420.1"
                            style={{ width: '100%' }}
                            addonAfter="V"
                          />
                        </Form.Item>
                      </Col>
                      <Col span={8}>
                        <Form.Item
                          name="current"
                          label="Current (A)"
                        >
                          <InputNumber
                            step={0.1}
                            placeholder="15.5"
                            style={{ width: '100%' }}
                            addonAfter="A"
                          />
                        </Form.Item>
                      </Col>
                      <Col span={8}>
                        <Form.Item
                          name="temperature"
                          label="Temperature (°C)"
                        >
                          <InputNumber
                            step={0.1}
                            placeholder="25.0"
                            style={{ width: '100%' }}
                            addonAfter="°C"
                          />
                        </Form.Item>
                      </Col>
                    </Row>

                    <Row gutter={16}>
                      <Col span={8}>
                        <Form.Item
                          name="cycle_count"
                          label="Cycle Count"
                        >
                          <InputNumber
                            min={0}
                            placeholder="150"
                            style={{ width: '100%' }}
                          />
                        </Form.Item>
                      </Col>
                      <Col span={8}>
                        <Form.Item
                          name="capacity_fade"
                          label="Capacity Fade (%)"
                        >
                          <InputNumber
                            min={0}
                            max={100}
                            step={0.1}
                            placeholder="5.0"
                            style={{ width: '100%' }}
                            addonAfter="%"
                          />
                        </Form.Item>
                      </Col>
                      <Col span={8}>
                        <Form.Item
                          name="internal_resistance"
                          label="Internal Resistance (Ω)"
                        >
                          <InputNumber
                            min={0}
                            step={0.001}
                            placeholder="0.05"
                            style={{ width: '100%' }}
                            addonAfter="Ω"
                          />
                        </Form.Item>
                      </Col>
                    </Row>

                    <Form.Item
                      name="measurement_timestamp"
                      label="Measurement Time"
                      rules={[{ required: true, message: 'Please select measurement time' }]}
                    >
                      <DatePicker
                        showTime
                        style={{ width: '100%' }}
                        format="YYYY-MM-DD HH:mm:ss"
                      />
                    </Form.Item>

                    <Form.Item>
                      <Button
                        type="primary"
                        htmlType="submit"
                        loading={loading}
                        icon={<PlusOutlined />}
                        size="large"
                      >
                        Add Battery Data
                      </Button>
                    </Form.Item>
                  </Form>
                </Card>
              )}

              {/* File Upload */}
              {uploadMode === 'file' && (
                <Card title="File Upload" style={{ marginBottom: 24 }}>
                  <Row gutter={24}>
                    <Col span={16}>
                      <Dragger
                        accept=".csv,.xlsx"
                        beforeUpload={handleFileUpload}
                        showUploadList={false}
                        disabled={loading}
                      >
                        <p className="ant-upload-drag-icon">
                          <InboxOutlined />
                        </p>
                        <p className="ant-upload-text">
                          Click or drag CSV/Excel file to upload
                        </p>
                        <p className="ant-upload-hint">
                          Support for CSV and Excel files with battery data
                        </p>
                      </Dragger>
                    </Col>
                    <Col span={8}>
                      <Alert
                        message="File Format"
                        description={
                          <div>
                            <p>Required columns:</p>
                            <ul>
                              <li><strong>state_of_health</strong> (required)</li>
                              <li><strong>measurement_timestamp</strong> (recommended)</li>
                            </ul>
                            <p>Optional columns: state_of_charge, voltage, current, temperature, cycle_count</p>
                            <Button 
                              type="link" 
                              icon={<DownloadOutlined />}
                              onClick={downloadTemplate}
                              style={{ padding: 0, marginTop: 8 }}
                            >
                              Download Template
                            </Button>
                          </div>
                        }
                        type="info"
                        showIcon
                      />
                    </Col>
                  </Row>
                </Card>
              )}

              {/* Recent Data */}
              <Card title="Recent Battery Data">
                {recentData.length > 0 ? (
                  <Table
                    columns={dataColumns}
                    dataSource={recentData}
                    rowKey="id"
                    pagination={false}
                    size="small"
                  />
                ) : (
                  <Alert
                    message="No data found"
                    description="Upload your first battery data to get started."
                    type="info"
                    showIcon
                  />
                )}
              </Card>
            </>
          )}
        </>
      )}
    </div>
  );
};

export default DataUpload;