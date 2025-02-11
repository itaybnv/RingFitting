function Coordinates10x=circle_contour_func_X10_no_shift(img1,x0,y0,rad_course,Borders,R,C)

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% this code gets the parameters of the ring at 1pix precision. it uses it as
% initial conditions for the search at high precision (0.1 pix) of the ring
% center and radius
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%rad_course=rad; %difference between ZringA input and ZringB input arg names
%img1 = img(:,:,1); 
%%%%%%%%%%%%%%%%%%%%%%%
% function input parameters:%
%%%%%%%%%%%%%%%%%%%%%%%

% I_fluor - image
% x0,y0,r - the ring's parameters that were found at 1pix precision
% search_area - search size in pixels

x02=x0+1; y02=y0+1; %We add 1 for the interpolation, because if we add more rows and columns than the center will also move.
search_area=1; %the search will be within 1 pixel (or 10 interpolated query points)
img1=double(img1);
I_fluor2(1:R+2,1:C+2) = img1((Borders(1)-1):(Borders(2)+1),(Borders(3)-1):(Borders(4)+1)); %expand the 31x31 pixels image to 33x33
% by adding more data from the large original image.
I_fluor2 = double(I_fluor2);
[R1,C1]=size(I_fluor2);
%% Interpolate the image (expand it's dimensions by X100) 


[X,Y] = meshgrid(1:1:R1); %1,2,3,4..
[XI,YI] = meshgrid(1:.1:R1); %1,1.1,1.2,1.3..
I_fluorI=interp2(X,Y,I_fluor2,XI,YI,'linear');
[R2,C2]=size(I_fluorI);


% Scan over all the circles and find the best coordinates and radius
RRR=rad_course*10-5:rad_course*10+5;
XXX=(x02*10-9)-search_area*5:(x02*10-9)+search_area*5;
YYY=(y02*10-9)-search_area*5:(y02*10-9)+search_area*5;

intensity=zeros((y02*10-9)+search_area*5,(x02*10-9)+search_area*5,rad_course*10+5); %intensity(y,x,z)
intensity10x_central_noshift=nan(11,11,11);
Count10x_central_noshift=nan(size(intensity10x_central_noshift));
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
                    % Find the area of intersection
                    int_mat(iy,ix) = I_fluorI(iy,ix);
                    area = CF_circle_square_intersection_area_2(centx, centy, rad, ix, iy, 1, 1, 100) / 0.5;
                    int = int + I_fluorI(iy,ix) * area;
                    count = count + area;
                 end
            end
            intensity(centy,centx,rad)=int/count; %calculates the average intensity along the circumference of each circle
            %intensity(centy,centx,rad)=int; %calculates the  total along the circumference of each circle
            intensity10x_central_noshift(Cy,Cx,Cr)=int;
            Count10x_central_noshift(Cy,Cx,Cr)=count;
        end
    end
end

[y_max_val,max_y]=max(intensity);
[max_val,max_x]=max(y_max_val);
[best_int_val,best_rad]=max(max_val);
best_x=max_x(1,1,best_rad); best_y=max_y(1,best_x,best_rad);
center_x=(best_x+9)/10-1; %rescaling from the interpolated grid to the original grid. why do we subtract 1? because we added earlier?
center_y=(best_y+9)/10-1;
rad_best = double(best_rad/10);

Coordinates10x=[center_x, center_y,rad_best];

% [maxValue, linearIndex] = max(intensity(:)); %find the winning combination and its index in a column vector of intensity
% [y, x, z] = ind2sub(size(intensity), linearIndex); % finding the coordinates using 'ind2sub'. [y,x,z] because intensity is also defined [y,x,z]
% intensity_vec=intensity(:); %all intensities
% intensity_vec(intensity_vec==0)=NaN;
% num_El=sum(~isnan(intensity_vec));
% h=histogram(intensity_vec);
return;