function Coordinates=circle_contour_func(i,radmin,radmax,cent_area)

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% this code finds a circle that fits the FtsZ ring the best. This is done
% by scanning the three parameters (center of the circle and radius) and
% averaging over the intensities of the image over the circle. The circle
% with the highest average intensity is the best fit.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%i=I_fluor(:,:,t); %difference between ZringA input and ZringB input arg names
%%%%%%%%%%%%%%%%%%%%%%%
% function input parameters:%
%%%%%%%%%%%%%%%%%%%%%%%
% i - image
% radmin - the smallest radius in the radius scan
% radmax - the largest radius in the radius scan
% cent_area - the size of a square over which it will search for the center
% of the circle.

I_fluor=i;        
I_fluor=double(I_fluor);
I_fluor1=I_fluor;
[R,C]=size(I_fluor);



centx= (R+1)/2; centy = (C+1)/2;


%% Scan over all the circles and find the best %

intensity1x_central=nan(numel(-(cent_area-1)/2:(cent_area-1)/2),numel(-(cent_area-1)/2:(cent_area-1)/2),numel(radmin:radmax));
Count1x_central=nan(size(intensity1x_central));
Cr=0;
for rad=radmin:radmax
    Cr=Cr+1;
    Cx=0;
    for indx= -(cent_area-1)/2:(cent_area-1)/2
    
        Cx=Cx+1;
        Cy=0;
        for indy= -(cent_area-1)/2:(cent_area-1)/2
        
            Cy=Cy+1;
            cenx=centx+indx; ceny=centy+indy;
            int=0;
            count=0;
            for ix=1:C
                 for iy=1:R
                    if(round(sqrt((ix-cenx)^2+(iy-ceny)^2))==rad)
                         int=int+I_fluor(iy,ix);
                         count=count+1;
                         I_fluor1(iy,ix)=0;
                    end
                 end
            end
            intensity((cent_area-1)/2+indy+1,(cent_area-1)/2+indx+1,rad)=int/count; %calculates the average intensity along the circumference of each circle
            %intensity((cent_area-1)/2+indy+1,(cent_area-1)/2+indx+1,rad)=int; %calculates the  total along the circumference of each circle
            intensity1x_central(Cy,Cx,Cr)=int;
            Count1x_central(Cy,Cx,Cr)=count;
        end
    end
end
[y_max_val,max_y]=max(intensity);
[max_val,max_x]=max(y_max_val);
[best_int_val,best_rad]=max(max_val);
best_x=max_x(1,1,best_rad); best_y=max_y(1,best_x,best_rad);
center_x=centx+best_x-((cent_area+1)/2); 
center_y=centy+best_y-((cent_area+1)/2);



Coordinates=[center_x, center_y,best_rad];
return;