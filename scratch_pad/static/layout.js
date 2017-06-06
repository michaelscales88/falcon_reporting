
    import React from 'react';
    import ReactDOM from 'react-dom';
    import { FilterChart as Component} from 'component_id';
    var charts = [{"options": {"chart_id": "mychart", "params": {"buffer": 8, "top": 40, "target": "#mychart", "animate_on_load": "true", "small_width_threshold": 160, "height": 200, "bottom": 30, "small_height_threshold": 120, "width": 450, "title": "Line Chart", "init_params": {"Data": "Steps"}, "transition_on_update": "true", "y_accessor": "y", "x_accessor": "x", "description": "Line Chart", "left": 40, "right": 40}, "url": "/mgchart/"}, "type": "MetricsGraphics"}];
var type = "FilterChart";
var filters = {"pyxley-filter": [{"options": {"label": "Data", "alias": "Data", "items": ["Calories Burned", "Steps", "Distance", "Floors", "Minutes Sedentary", "Minutes Lightly Active", "Minutes Fairly Active", "Minutes Very Active", "Activity Calories"], "default": "Steps"}, "type": "SelectButton"}]};
    ReactDOM.render(
        <Component
        charts = { charts }
type = { type }
filters = { filters } />,
        document.getElementById("./static/bower_components/pyxley/build/pyxley.js")
    );
    