
# *Image Analysis and Data Processing*

For efficiency, we begin analysis by downsizing video files and
importing them into Fiji. Using SpeckleTrackerJ, we then extract
particle positions over time, which we can then rescale to
original size and convert to particle ``tracks'' (a more
organized particle position/time format). For each track we then
extract various particle features: Namely, mean
Straight-Line-Speed (displacement / time). To attempt to filter
out ``stuck'' particles in non-control experiments, we remove
any particle whose mean SLS is less than the associated mean
control value. At this point all data values are still in terms
of pixels and frames, which we can then convert back to original
units.
