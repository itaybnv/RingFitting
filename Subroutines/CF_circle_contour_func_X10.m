function CenteredImg=circle_contour_func_X10(img,x0,y0,rad_course,gap,Borders,R,C)

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% this code gets the parameters of the ring at 1pix precision. it uses it as
% initial conditions for the search at high precision (0.1 pix) of the ring
% center and radius
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%%%%%%%%%%%%%%%%%%%%
% function input parameters:%
%rad_course=rad; %difference between ZringA input and ZringB input arg names
%img1 = img(:,:,1); 
%%%%%%%%%%%%%%%%%%%%%%%

% I_fluor - image
% x0,y0,r - the ring's parameters that were found at 1pix precision
% search_area - search size in pixels

x02=x0+gap; y02=y0+gap;
search_area=1;
img=double(img);
I_fluor2(1:R+gap*2,1:C+gap*2) = img((Borders(1)-gap):(Borders(2)+gap),(Borders(3)-gap):(Borders(4)+gap));  %image with [x0_matlab+gap,y0_matlab+gap] 
% (1x center) as the center. Since the center is shifted (by gap), the borders are
% re-adjusted accordingly. the final image is still 31x31 pixels
I_fluor2 = double(I_fluor2);
[R1,C1]=size(I_fluor2);


%% Interpolate the image (expand it's dimensions by X100) 


[X,Y] = meshgrid(1:1:R1); % 1,2,3,4,5
[XI,YI] = meshgrid(1:.1:R1); %1,1.1,1.2,1.3,1.4..
I_fluorI=interp2(X,Y,I_fluor2,XI,YI,'linear');
[R2,C2]=size(I_fluorI);


% Scan over all the circles and find the best %

intensity=zeros((y02*10-9)+search_area*5,(x02*10-9)+search_area*5,rad_course*10+5);
intensity10x_central=nan(11,11,11);
Count10x_central=nan(size(intensity10x_central));
Cr=0;
int_mat=[]; factor =1.2;
for rad=rad_course*10-5:rad_course*10+5
    Cr=Cr+1;
    Cx=0;
    for centx=(x02*10-9)-search_area*5:(x02*10-9)+search_area*5
        Cx=Cx+1;
        Cy=0;
        for centy=(y02*10-9)-search_area*5:(y02*10-9)+search_area*5
           Cy=Cy+1;           
            int=0;
            count=0;
            for ix=x02*10-9-round(rad*factor):x02*10-9+round(rad*factor)
                 for iy=y02*10-9-round(rad*factor):y02*10-9+round(rad*factor)
                    if(round(sqrt((ix-centx)^2+(iy-centy)^2))==rad)
                         int_mat(iy,ix) = I_fluorI(iy,ix);
                         int=int+I_fluorI(iy,ix);
                         count=count+1;
                        
                    end
                 end
            end

            intensity(centy,centx,rad)=int/count; %calculates the average intensity along the circumference of each circle
            %intensity(centy,centx,rad)=int; %calculates the  total along the circumference of each circle
            intensity10x_central(Cy,Cx,Cr)=int;
            Count10x_central(Cy,Cx,Cr)=count;
        end
    end
    % int_mat(int_mat==0)=NaN;
    % figure; surf(int_mat,'EdgeColor','none');

end

[y_max_val,max_y]=max(intensity);
[max_val,max_x]=max(y_max_val);
[best_int_val,best_rad]=max(max_val);
best_x=max_x(1,1,best_rad); best_y=max_y(1,best_x,best_rad);
center_x=best_x; 
center_y=best_y;
rad_best = best_rad/10;

%% generate a new matrix, similar in size to the original I_fluor, where the 
% ring is centered at the middle of the matrix. This matrix is the result
% of this whole function



R3=R1-2*gap; C3=C1-2*gap;

for ii=-(R3-1)/2:(R3-1)/2
    for jj=-(R3-1)/2:(R3-1)/2        
        I_flour_cent(R3-(R3-1)/2+jj,R3-(R3-1)/2+ii)=I_fluorI(center_y+10*jj,center_x+10*ii);
    end
end


CenteredImg=I_flour_cent;
return;
    % 
    % rad=89;
    % ix=x02*10-9-round(rad*factor):x02*10-9+round(rad*factor);
    % iy=y02*10-9-round(rad*factor):y02*10-9+round(rad*factor);
    % 
    % %scatter3
    % % Get the size of the matrix
    % [rows, cols] = size(int_mat);
    % 
    % % Generate the x and y coordinates
    % [x, y] = meshgrid(1:cols, 1:rows);
    % 
    % % Convert the matrix to column vectors for scatter3
    % x = x(:);
    % y = y(:);
    % z = int_mat(:);  % Use the pixel values as the z-coordinates
    % 
    % % Plot using scatter3
    % figure;scatter3(x, y, z, 'filled');
    % xlabel('x');ylabel('y');zlabel('intensity');