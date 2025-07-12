/**
 * Node Configuration Panel - Configure pipeline node settings
 */
import React, { useState, useEffect } from 'react';
import { 
  X, 
  Save, 
  AlertCircle, 
  CheckCircle, 
  Settings,
  Database,
  Filter,
  Brain,
  BarChart3,
  Plus,
  Minus
} from 'lucide-react';

const ConfigField = ({ field, value, onChange, schema }) => {
  const handleChange = (newValue) => {
    onChange(field, newValue);
  };

  switch (schema.type) {
    case 'text':
      return (
        <input
          type="text"
          value={value || ''}
          onChange={(e) => handleChange(e.target.value)}
          placeholder={schema.placeholder || `Enter ${field}`}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          required={schema.required}
        />
      );

    case 'password':
      return (
        <input
          type="password"
          value={value || ''}
          onChange={(e) => handleChange(e.target.value)}
          placeholder={schema.placeholder || `Enter ${field}`}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          required={schema.required}
        />
      );

    case 'textarea':
      return (
        <textarea
          value={value || ''}
          onChange={(e) => handleChange(e.target.value)}
          placeholder={schema.placeholder || `Enter ${field}`}
          rows={4}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
          required={schema.required}
        />
      );

    case 'select':
      return (
        <select
          value={value || schema.default || ''}
          onChange={(e) => handleChange(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          required={schema.required}
        >
          {!schema.required && <option value="">Select {field}</option>}
          {schema.options?.map((option) => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}
        </select>
      );

    case 'multi_select':
      return (
        <div className="space-y-2">
          {schema.options?.map((option) => (
            <label key={option} className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={(value || []).includes(option)}
                onChange={(e) => {
                  const currentValue = value || [];
                  if (e.target.checked) {
                    handleChange([...currentValue, option]);
                  } else {
                    handleChange(currentValue.filter(v => v !== option));
                  }
                }}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="text-sm text-gray-700">{option}</span>
            </label>
          ))}
        </div>
      );

    case 'number':
      return (
        <input
          type="number"
          value={value || schema.default || ''}
          onChange={(e) => handleChange(parseFloat(e.target.value) || 0)}
          min={schema.min}
          max={schema.max}
          step={schema.step || 1}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          required={schema.required}
        />
      );

    case 'boolean':
      return (
        <label className="flex items-center space-x-2">
          <input
            type="checkbox"
            checked={value !== undefined ? value : schema.default}
            onChange={(e) => handleChange(e.target.checked)}
            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
          />
          <span className="text-sm text-gray-700">Enable {field}</span>
        </label>
      );

    case 'key_value':
      const keyValuePairs = value || {};
      return (
        <div className="space-y-2">
          {Object.entries(keyValuePairs).map(([key, val], index) => (
            <div key={index} className="flex space-x-2">
              <input
                type="text"
                value={key}
                onChange={(e) => {
                  const newPairs = { ...keyValuePairs };
                  delete newPairs[key];
                  newPairs[e.target.value] = val;
                  handleChange(newPairs);
                }}
                placeholder="Key"
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <input
                type="text"
                value={val}
                onChange={(e) => {
                  handleChange({
                    ...keyValuePairs,
                    [key]: e.target.value
                  });
                }}
                placeholder="Value"
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <button
                onClick={() => {
                  const newPairs = { ...keyValuePairs };
                  delete newPairs[key];
                  handleChange(newPairs);
                }}
                className="p-2 text-red-500 hover:bg-red-50 rounded-lg"
              >
                <Minus className="w-4 h-4" />
              </button>
            </div>
          ))}
          <button
            onClick={() => {
              handleChange({
                ...keyValuePairs,
                '': ''
              });
            }}
            className="flex items-center space-x-2 px-3 py-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
          >
            <Plus className="w-4 h-4" />
            <span>Add pair</span>
          </button>
        </div>
      );

    case 'json':
      return (
        <textarea
          value={typeof value === 'string' ? value : JSON.stringify(value || {}, null, 2)}
          onChange={(e) => {
            try {
              const parsed = JSON.parse(e.target.value);
              handleChange(parsed);
            } catch {
              handleChange(e.target.value);
            }
          }}
          placeholder={`{"key": "value"}`}
          rows={6}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm resize-none"
        />
      );

    case 'file':
      return (
        <div className="space-y-2">
          <input
            type="file"
            onChange={(e) => {
              const file = e.target.files[0];
              if (file) {
                handleChange(file.name);
              }
            }}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            accept=".csv,.xlsx,.json"
          />
          {value && (
            <p className="text-sm text-gray-600">Selected: {value}</p>
          )}
        </div>
      );

    default:
      return (
        <input
          type="text"
          value={value || ''}
          onChange={(e) => handleChange(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      );
  }
};

const NodeConfigPanel = ({ node, onConfigChange, onClose, isMobile }) => {
  const [config, setConfig] = useState(node.config || {});
  const [hasChanges, setHasChanges] = useState(false);
  const [validationErrors, setValidationErrors] = useState({});

  useEffect(() => {
    setConfig(node.config || {});
    setHasChanges(false);
    setValidationErrors({});
  }, [node]);

  const getNodeIcon = (type) => {
    const iconMap = {
      'source': <Database className="w-5 h-5" />,
      'transform': <Filter className="w-5 h-5" />,
      'validate': <CheckCircle className="w-5 h-5" />,
      'ai': <Brain className="w-5 h-5" />,
      'output': <BarChart3 className="w-5 h-5" />
    };
    return iconMap[type] || <Settings className="w-5 h-5" />;
  };

  const handleFieldChange = (field, value) => {
    const newConfig = { ...config, [field]: value };
    setConfig(newConfig);
    setHasChanges(true);
    
    // Clear validation error for this field
    if (validationErrors[field]) {
      setValidationErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  const validateConfig = () => {
    const errors = {};
    
    // Add validation logic based on node type and schema
    // This is a simplified example
    Object.entries(config).forEach(([field, value]) => {
      if (!value && field.includes('required')) {
        errors[field] = 'This field is required';
      }
    });
    
    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSave = () => {
    if (validateConfig()) {
      onConfigChange(config);
      setHasChanges(false);
    }
  };

  const handleReset = () => {
    setConfig(node.config || {});
    setHasChanges(false);
    setValidationErrors({});
  };

  // Mock schema - in real implementation, this would come from the node template
  const getConfigSchema = () => {
    const schemas = {
      'csv_source': {
        file_path: { type: 'file', required: true },
        delimiter: { type: 'select', options: [',', ';', '\t'], default: ',' },
        encoding: { type: 'select', options: ['utf-8', 'latin-1'], default: 'utf-8' },
        has_header: { type: 'boolean', default: true }
      },
      'database_source': {
        db_type: { type: 'select', options: ['postgresql', 'mysql', 'sqlite'], required: true },
        host: { type: 'text', required: true },
        database: { type: 'text', required: true },
        username: { type: 'text', required: true },
        password: { type: 'password', required: true },
        query: { type: 'textarea', required: true }
      },
      'data_cleaning': {
        missing_strategy: { type: 'select', options: ['drop', 'fill', 'forward_fill'], default: 'drop' },
        fill_value: { type: 'text', default: '0' },
        remove_duplicates: { type: 'boolean', default: true },
        trim_whitespace: { type: 'boolean', default: true }
      }
    };
    
    return schemas[node.name?.toLowerCase().replace(' ', '_')] || {};
  };

  const configSchema = getConfigSchema();

  return (
    <div className="h-full flex flex-col bg-white">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        <div className="flex items-center space-x-3">
          <div className="flex-shrink-0">
            {node.icon ? (
              <span className="text-xl">{node.icon}</span>
            ) : (
              getNodeIcon(node.type)
            )}
          </div>
          <div>
            <h2 className="text-lg font-semibold text-gray-900">{node.name}</h2>
            <p className="text-sm text-gray-500">{node.type} node</p>
          </div>
        </div>
        
        <button
          onClick={onClose}
          className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Configuration Form */}
      <div className="flex-1 overflow-y-auto p-4">
        <div className="space-y-6">
          {/* Node Description */}
          <div className="bg-gray-50 p-3 rounded-lg">
            <p className="text-sm text-gray-700">{node.description}</p>
          </div>

          {/* Configuration Fields */}
          {Object.keys(configSchema).length > 0 ? (
            Object.entries(configSchema).map(([field, schema]) => (
              <div key={field}>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {field.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  {schema.required && <span className="text-red-500 ml-1">*</span>}
                </label>
                
                <ConfigField
                  field={field}
                  value={config[field]}
                  onChange={handleFieldChange}
                  schema={schema}
                />
                
                {validationErrors[field] && (
                  <p className="mt-1 text-sm text-red-600 flex items-center space-x-1">
                    <AlertCircle className="w-4 h-4" />
                    <span>{validationErrors[field]}</span>
                  </p>
                )}
                
                {schema.description && (
                  <p className="mt-1 text-xs text-gray-500">{schema.description}</p>
                )}
              </div>
            ))
          ) : (
            <div className="text-center py-8">
              <Settings className="w-12 h-12 text-gray-300 mx-auto mb-3" />
              <p className="text-gray-500">No configuration required</p>
              <p className="text-xs text-gray-400 mt-1">
                This node works with default settings
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-gray-200 bg-gray-50">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            {hasChanges ? (
              <div className="flex items-center space-x-1 text-orange-600">
                <AlertCircle className="w-4 h-4" />
                <span className="text-sm">Unsaved changes</span>
              </div>
            ) : (
              <div className="flex items-center space-x-1 text-green-600">
                <CheckCircle className="w-4 h-4" />
                <span className="text-sm">Saved</span>
              </div>
            )}
          </div>
          
          <div className="flex space-x-2">
            {hasChanges && (
              <button
                onClick={handleReset}
                className="px-3 py-2 text-sm text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors"
              >
                Reset
              </button>
            )}
            
            <button
              onClick={handleSave}
              disabled={!hasChanges}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <Save className="w-4 h-4" />
              <span>Save</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NodeConfigPanel;
