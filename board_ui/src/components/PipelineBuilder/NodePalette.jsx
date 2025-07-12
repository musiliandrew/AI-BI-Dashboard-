/**
 * Node Palette - Draggable components for pipeline building
 */
import React, { useState } from 'react';
import { useDrag } from 'react-dnd';
import { 
  ChevronDown, 
  ChevronRight, 
  Search,
  Database,
  Filter,
  CheckCircle,
  Brain,
  BarChart3,
  FileText,
  Globe,
  Zap
} from 'lucide-react';

const DraggableNode = ({ nodeTemplate, onAddNode, isMobile }) => {
  const [{ isDragging }, drag] = useDrag({
    type: 'node',
    item: { 
      type: 'node', 
      nodeType: nodeTemplate.id,
      template: nodeTemplate 
    },
    end: (item, monitor) => {
      const dropResult = monitor.getDropResult();
      if (item && dropResult && onAddNode) {
        onAddNode(item.nodeType, dropResult.position || { x: 100, y: 100 });
      }
    },
    collect: (monitor) => ({
      isDragging: monitor.isDragging(),
    }),
  });

  const getNodeIcon = (type) => {
    const iconMap = {
      'source': <Database className="w-4 h-4" />,
      'transform': <Filter className="w-4 h-4" />,
      'validate': <CheckCircle className="w-4 h-4" />,
      'ai': <Brain className="w-4 h-4" />,
      'output': <BarChart3 className="w-4 h-4" />
    };
    return iconMap[type] || <FileText className="w-4 h-4" />;
  };

  const getNodeColor = (type) => {
    const colorMap = {
      'source': 'bg-blue-50 border-blue-200 text-blue-700',
      'transform': 'bg-green-50 border-green-200 text-green-700',
      'validate': 'bg-yellow-50 border-yellow-200 text-yellow-700',
      'ai': 'bg-purple-50 border-purple-200 text-purple-700',
      'output': 'bg-orange-50 border-orange-200 text-orange-700'
    };
    return colorMap[type] || 'bg-gray-50 border-gray-200 text-gray-700';
  };

  const handleClick = () => {
    if (isMobile && onAddNode) {
      // On mobile, tap to add node at default position
      onAddNode(nodeTemplate.id, { x: 100, y: 100 });
    }
  };

  return (
    <div
      ref={!isMobile ? drag : null}
      onClick={handleClick}
      className={`
        p-3 border rounded-lg cursor-pointer transition-all duration-200
        ${getNodeColor(nodeTemplate.type)}
        ${isDragging ? 'opacity-50 scale-95' : 'hover:shadow-md hover:scale-105'}
        ${isMobile ? 'active:scale-95' : ''}
      `}
      style={{ opacity: isDragging ? 0.5 : 1 }}
    >
      <div className="flex items-start space-x-3">
        <div className="flex-shrink-0 mt-0.5">
          {nodeTemplate.icon ? (
            <span className="text-lg">{nodeTemplate.icon}</span>
          ) : (
            getNodeIcon(nodeTemplate.type)
          )}
        </div>
        
        <div className="flex-1 min-w-0">
          <h4 className="text-sm font-medium truncate">
            {nodeTemplate.name}
          </h4>
          <p className="text-xs opacity-75 mt-1 line-clamp-2">
            {nodeTemplate.description}
          </p>
        </div>
      </div>
      
      {isMobile && (
        <div className="mt-2 text-xs opacity-60">
          Tap to add to canvas
        </div>
      )}
    </div>
  );
};

const CategorySection = ({ category, nodes, onAddNode, isMobile, isExpanded, onToggle }) => {
  const getCategoryIcon = (category) => {
    const iconMap = {
      'Data Sources': <Database className="w-4 h-4" />,
      'Data Processing': <Filter className="w-4 h-4" />,
      'Data Validation': <CheckCircle className="w-4 h-4" />,
      'AI & Analytics': <Brain className="w-4 h-4" />,
      'Outputs': <BarChart3 className="w-4 h-4" />
    };
    return iconMap[category] || <FileText className="w-4 h-4" />;
  };

  return (
    <div className="mb-4">
      <button
        onClick={onToggle}
        className="w-full flex items-center justify-between p-2 text-left hover:bg-gray-50 rounded-lg transition-colors"
      >
        <div className="flex items-center space-x-2">
          {getCategoryIcon(category)}
          <span className="font-medium text-gray-900">{category}</span>
          <span className="text-xs text-gray-500">({nodes.length})</span>
        </div>
        {isExpanded ? (
          <ChevronDown className="w-4 h-4 text-gray-400" />
        ) : (
          <ChevronRight className="w-4 h-4 text-gray-400" />
        )}
      </button>
      
      {isExpanded && (
        <div className="mt-2 space-y-2 pl-2">
          {nodes.map((node) => (
            <DraggableNode
              key={node.id}
              nodeTemplate={node}
              onAddNode={onAddNode}
              isMobile={isMobile}
            />
          ))}
        </div>
      )}
    </div>
  );
};

const NodePalette = ({ nodeTemplates, onAddNode, isMobile }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [expandedCategories, setExpandedCategories] = useState({
    'Data Sources': true,
    'Data Processing': true,
    'AI & Analytics': false,
    'Data Validation': false,
    'Outputs': false
  });

  const toggleCategory = (category) => {
    setExpandedCategories(prev => ({
      ...prev,
      [category]: !prev[category]
    }));
  };

  const filteredTemplates = React.useMemo(() => {
    if (!searchTerm) return nodeTemplates;
    
    const filtered = {};
    Object.keys(nodeTemplates).forEach(category => {
      const filteredNodes = nodeTemplates[category].filter(node =>
        node.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        node.description.toLowerCase().includes(searchTerm.toLowerCase())
      );
      if (filteredNodes.length > 0) {
        filtered[category] = filteredNodes;
      }
    });
    return filtered;
  }, [nodeTemplates, searchTerm]);

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900 mb-3">
          Pipeline Components
        </h2>
        
        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search components..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
        
        {!isMobile && (
          <p className="text-xs text-gray-500 mt-2">
            Drag components to the canvas to build your pipeline
          </p>
        )}
        
        {isMobile && (
          <p className="text-xs text-gray-500 mt-2">
            Tap components to add them to your pipeline
          </p>
        )}
      </div>

      {/* Categories */}
      <div className="flex-1 overflow-y-auto p-4">
        {Object.keys(filteredTemplates).length === 0 ? (
          <div className="text-center py-8">
            <FileText className="w-12 h-12 text-gray-300 mx-auto mb-3" />
            <p className="text-gray-500">No components found</p>
            <p className="text-xs text-gray-400 mt-1">
              Try adjusting your search terms
            </p>
          </div>
        ) : (
          Object.keys(filteredTemplates).map((category) => (
            <CategorySection
              key={category}
              category={category}
              nodes={filteredTemplates[category]}
              onAddNode={onAddNode}
              isMobile={isMobile}
              isExpanded={expandedCategories[category]}
              onToggle={() => toggleCategory(category)}
            />
          ))
        )}
      </div>

      {/* Quick Actions */}
      <div className="p-4 border-t border-gray-200 bg-gray-50">
        <div className="space-y-2">
          <button className="w-full flex items-center space-x-2 p-2 text-sm text-blue-600 hover:bg-blue-50 rounded-lg transition-colors">
            <Zap className="w-4 h-4" />
            <span>AI Recommendations</span>
          </button>
          
          <button className="w-full flex items-center space-x-2 p-2 text-sm text-purple-600 hover:bg-purple-50 rounded-lg transition-colors">
            <Globe className="w-4 h-4" />
            <span>Browse Templates</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default NodePalette;
