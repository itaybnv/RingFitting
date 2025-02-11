function area = computeIntersectionArea(xc, yc, r, xs, ys, w, h, gridSize)
    % Compute the area of intersection between a circle and a square using a grid approximation.
    % Inputs:
    %   xc, yc: Center of the circle
    %   r: Radius of the circle
    %   gridSize: Number of grid points along each axis (higher = more accurate but slower)
    % Output:
    %   area: Approximate area of intersection

    % Create a grid of points within the square [-1, 1] x [-1, 1]
    x = linspace(xs - w/2, xs + w/2, gridSize);
    y = linspace(ys - h/2, ys + h/2, gridSize);
    [X, Y] = meshgrid(x, y);

    % Evaluate the indicator function on the grid
    insideCircle = (X - xc).^2 + (Y - yc).^2 <= r^2;

    % Compute the area by summing the points inside the circle and scaling by grid cell area
    cellArea = (2 / (gridSize - 1))^2; % Area of each grid cell
    area = sum(insideCircle(:)) * cellArea;
    if area > w * h / 2
        area = w * h - area;
    end
end